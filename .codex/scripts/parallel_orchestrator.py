from __future__ import annotations

import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List


def parse_contract_from_jsonl(stdout: str) -> Dict[str, Any]:
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        event = json.loads(line)
        if event.get("type") != "item.completed":
            continue

        item = event.get("item") or {}
        if item.get("type") != "agent_message":
            continue

        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            continue

        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("Contract JSON is not an object")
        return data

    raise ValueError("No agent_message JSON contract found in JSONL stream")


def run_agent(scope: str, task: str) -> Dict[str, Any]:
    start = time.time()
    prompt = f"""
Analyze ONLY files under {scope}.
Task: {task}

Keep it short (max ~5 bullets). No extra commentary.

Return STRICT JSON:
{{
"status": "success|partial|failed",
"summary": "string",
"findings": ["string"],
"files_read": ["string"],
"files_modified": ["string"]
}}
""".strip()

    proc = subprocess.run(
        ["codex", "-a", "never", "-s", "workspace-write", "exec", "--json", prompt],
        capture_output=True,
        text=True,
    )
    runtime_ms = int((time.time() - start) * 1000)

    exit_code = proc.returncode
    stderr = (proc.stderr or "").strip()
    stdout = (proc.stdout or "").strip()

    try:
        data = parse_contract_from_jsonl(stdout)
    except Exception as e:
        return {
            "status": "failed",
            "summary": f"Invalid JSON output (exit={exit_code})",
            "findings": [],
            "files_read": [],
            "files_modified": [],
            "runtime_ms": runtime_ms,
            "scope": scope,
            "reason": "invalid_json",
            "error": str(e),
            "exit_code": exit_code,
            "stderr": stderr,
            "raw_stdout": stdout,
        }

    data["runtime_ms"] = runtime_ms
    data["scope"] = scope
    data["exit_code"] = exit_code

    if exit_code != 0 and not data.get("reason"):
        data["reason"] = "nonzero_exit"
        data["error"] = stderr

    return data


def aggregate(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    combined: Dict[str, Any] = {
        "status": "success",
        "summaries": [],
        "findings": [],
        "failures": [],
    }
    failed_count = 0
    for r in results:
        if r.get("status") == "failed":
            combined["status"] = "partial"
            failed_count += 1
            combined["failures"].append({
                "scope": r.get("scope"),
                "summary": r.get("summary"),
                "runtime_ms": r.get("runtime_ms"),
                "reason": r.get("reason"),
                "error": r.get("error"),
                "exit_code": r.get("exit_code")
            })
        
        else:
            combined["summaries"].append({
                "scope": r.get("scope"),
                "summary": r.get("summary")
            })
            
            combined["findings"].extend(
                [
                    {"scope": r.get("scope"), "finding": f}
                    for f in r.get("findings", [])
                ]
            )

    if failed_count == len(results):
        combined["status"] = "failed"

    return combined


if __name__ == "__main__":
    jobs = [
        (
            "packages/excalidraw/renderer/",
            "List 3 correctness or performance risks you can infer.",
        ),
        (
            "excalidraw-app/components/",
            "List 3 UI edge cases worth testing.",
        ),
        (
            "packages/excalidraw/",
            "List 3 maintainability issues (naming, structure, coupling) you notice.",
        ),
    ]

    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futures = [pool.submit(run_agent, scope, task) for scope, task in jobs]
        for fut in as_completed(futures):
            results.append(fut.result())

    out = aggregate(results)
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/deterministic_summary.json").write_text(
        json.dumps(out, indent=2),
        encoding="utf-8",
    )
    print("Wrote artifacts/deterministic_summary.json")