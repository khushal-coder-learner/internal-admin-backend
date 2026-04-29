# Deployment Readiness Checklist

Use this reference when a readiness assessment needs more structure than the main skill body.

## 1. Runtime Topology

- Identify every deployable unit: frontend, API, worker, scheduler, migration job, database, Redis, object storage, reverse proxy.
- Identify which units are user-facing and which are internal.
- Identify whether services can scale independently.

## 2. Configuration And Secrets

- Verify environment variables exist for runtime-only values.
- Flag hardcoded `localhost`, fixed ports, and provider-specific assumptions.
- Flag `.env` coupling that would break in managed platforms.
- Flag secrets in repo, logs, debug prints, or seeded defaults.

## 3. Persistent Database

- Verify migration command and migration ownership.
- Verify production startup does not depend on manual local steps.
- Check whether seed/admin bootstrap runs automatically and whether that is safe.
- Check connection-string portability, SSL requirements, and pool behavior when relevant.
- Ask whether backups, restore, and maintenance are owned by the platform or the team.

## 4. In-Memory Datastore

First determine the datastore role.

- Cache only: availability matters, but data loss may be acceptable.
- Queue/session/lock/rate-limit/token store: treat as correctness-critical.

For Redis-like systems, check:

- queue durability expectations
- startup recovery behavior
- lock expiry assumptions
- handling of datastore restarts
- auth/session invalidation behavior

## 5. Worker And Async Jobs

- Verify how jobs are enqueued.
- Verify where job state lives.
- Verify retries, backoff, and idempotency expectations.
- Verify crash recovery and duplicate-processing safeguards.
- Verify whether pending jobs survive service or Redis restarts.

## 6. File And Object Storage

- Identify uploads, exports, reports, or generated artifacts.
- Flag local-disk storage inside containers unless a persistent volume is clearly intended.
- Prefer object storage for user-facing downloads in cloud environments.
- Verify signed URL generation uses deployment-aware base URLs or provider-native URLs.

## 7. Frontend

- Verify a production build command exists.
- Verify API base URL is environment-driven.
- Verify route hosting assumptions for SPA routing if relevant.
- Verify auth token storage approach and note risk if tokens live in browser storage.
- Verify CORS and cookie strategy match the chosen deployment model.

## 8. Backend API

- Verify entrypoint, health checks, and production server command.
- Verify logs are structured enough for cloud observability.
- Flag dev-only middleware, verbose debug output, and import-time side effects.
- Verify request origin handling, proxy awareness, and file/path assumptions when relevant.

## 9. Deployment Mechanics

- Verify Dockerfiles are production-oriented rather than only dev-oriented.
- Flag bind mounts, dev reload flags, and local seed flows in production paths.
- Check whether CI/CD, image build, and release steps are defined or missing.
- Check whether migrations run as a separate release step or are coupled unsafely to app boot.

## 10. Verdict Rubric

- `Ready`: core runtime, config, persistence, and recovery assumptions are production-safe.
- `Conditionally ready`: platform fit is clear, but a short list of concrete fixes remains.
- `Not ready`: deploy would likely fail, lose data, expose secrets, or break operationally.

## 11. Deliverables

A strong assessment usually includes:

- a one-paragraph verdict
- the actual runtime topology
- the biggest blockers
- a recommended deployment shape
- a short pre-deploy checklist
- explicit unknowns or unverified areas
