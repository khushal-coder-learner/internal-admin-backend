import os
from pathlib import Path


def get_export_dir() -> Path:
    export_dir = Path(os.getenv("EXPORT_DIR", "/data/exports")).resolve()
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def resolve_export_path(path: str | Path) -> Path:
    requested_path = Path(path).resolve()
    requested_path.relative_to(get_export_dir())
    return requested_path
