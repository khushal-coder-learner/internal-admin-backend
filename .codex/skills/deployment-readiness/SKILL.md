---
name: deployment-readiness
description: Assess whether a web application is ready to deploy to cloud infrastructure. Use when Codex needs to evaluate or explain deployment readiness for systems with a frontend, backend API, background workers, persistent databases, in-memory datastores such as Redis, file storage, or container-based runtimes; when comparing local Docker setup to production requirements; or when producing a readiness checklist, risk report, or next-step deployment plan.
---

# Deployment Readiness

## Overview

Assess deploy readiness by mapping the full runtime shape of the app, identifying blockers, and separating production requirements from local-development conveniences.

Ground the assessment in the actual repo before giving recommendations. Prefer concrete findings with file references over generic cloud advice.

## Workflow

1. Inspect the repository layout and identify deployable units.
2. Map each unit to its runtime role.
3. Check configuration, startup, persistence, networking, and operational readiness.
4. Classify findings into blockers, important gaps, and follow-up improvements.
5. End with a practical deployment path, not just a checklist.

## Inspect First

Read only the files needed to answer the question. Start with:

- Root and service-level `README`, `docker-compose`, `Dockerfile`, dependency manifests, env examples, CI files, and deployment configs.
- Backend entrypoints, config/settings, DB session setup, health checks, storage paths, auth/session handling, worker/queue code, and migration setup.
- Frontend build config, API base URL wiring, auth storage, and environment-variable usage.

If the user asks a conceptual question, explain the concept first, then map it back to the repo if code is available.

## Evaluate By System Role

Treat each component according to what failure means in production:

- Persistent database: verify migrations, connection config, backup/restore expectations, SSL posture, seed/init behavior, and operational ownership.
- In-memory datastore: determine whether it is only a cache or part of the app's correctness path. If it supports queues, sessions, token replay protection, locks, or rate limiting, treat it as operationally critical.
- Worker or scheduler: verify startup path, retry behavior, idempotency expectations, crash recovery, and whether jobs survive restarts.
- File storage: determine whether local disk is acceptable. Flag exports, uploads, or generated files stored on ephemeral container filesystems.
- Frontend: verify production build path, public API URL configuration, asset hosting expectations, and auth-storage risk.
- Backend API: verify environment-only config, CORS/origin handling, health checks, logging, secrets handling, and production server assumptions.

Read [references/readiness-checklist.md](references/readiness-checklist.md) when you need the fuller rubric.

## Decision Rules

Do not call an app "ready" just because it runs locally.

Call it:

- `Ready`: no material blockers for a first managed-cloud deployment; only low-risk cleanup remains.
- `Conditionally ready`: deployable with a short list of concrete fixes.
- `Not ready`: missing or unsafe foundations around config, persistence, startup, secrets, recovery, or runtime topology.

Always distinguish:

- What is already strong.
- What would break or become risky in cloud.
- What must be fixed before first deploy.
- What can wait until after launch.

## Output Shape

Prefer this structure:

1. One-paragraph verdict.
2. `What deploy readiness means for this app`.
3. `What looks ready already`.
4. `What still blocks or weakens deployment`.
5. `Recommended deployment shape`.
6. `Next steps`.

When findings are numerous, order them by severity and include file references.

## Guidance

- Tie every important conclusion to code or config evidence when possible.
- Separate developer-experience choices from production requirements.
- Note when a repo is optimized for local Docker rather than cloud deployment.
- Be explicit about hidden dependencies such as migrations, bootstrap scripts, seeds, cron-like loops, and shared storage assumptions.
- Call out localhost assumptions, hardcoded URLs, debug prints, committed secrets, and local bind mounts.
- Mention test and verification gaps if you did not run builds, tests, or containers.
