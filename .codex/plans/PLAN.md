# Minimal Patch Plan: Production-Ready Export Downloads

## Summary
Fix the export download pipeline by making file storage a single shared runtime concern across API and worker, and by removing the hard-coded download path mismatch. Keep the current job flow and frontend behavior, but make the download URL and file-serving logic use the same configured export root.

## Key Changes
- Make `backend/app/services/exports/paths.py` the single source of truth for the export directory.
  - Keep `get_export_dir()` as the canonical resolver for `EXPORT_DIR`.
  - Remove the `print(get_export_dir())` import-time side effect.
  - Add a small helper for safe path validation so the download endpoint checks membership against the resolved export root instead of using string `startswith`.

- Patch the download-serving path in `backend/app/api/jobs.py`.
  - Replace the hard-coded `Path("/data/exports")` check with the shared export-dir helper.
  - Keep the existing signed-download route and response shape.
  - Keep `FileResponse` behavior unchanged.
  - Preserve the current short-lived signed URL model, but validate the requested path against the resolved export root before serving.

- Make signed URL generation deployment-controlled.
  - Update `backend/app/utils/file_utils.py` to build the signed URL from `settings.exports_download_url` instead of `request.url_for(...)`.
  - Remove the `Request` dependency from URL generation and from job-list/job-detail handlers if it is no longer needed elsewhere.
  - Keep the returned `download_url` field unchanged for clients.

- Fix the production runtime topology.
  - In `backend/docker-compose.yml`, add one named volume for exports and mount it into both `api` and `worker` at the same path.
  - Mount it read-write in `worker` and read-only in `api`.
  - Add `EXPORT_DIR=/data/exports` to the shared backend env so both services resolve the same location.
  - Leave the existing Dockerfile user/permission setup in place; only adjust it if needed to make `/data/exports` writable by the app user.

## Public Interfaces / Config
- No route changes: keep `POST /jobs/export`, `GET /jobs/me`, `GET /jobs/{job_id}`, and `GET /exports/download` as they are.
- No frontend contract changes: keep `download_url` in job responses.
- Configuration changes:
  - `EXPORT_DIR` becomes required operational config for API and worker, with `/data/exports` as the default deployment value.
  - `EXPORTS_DOWNLOAD_URL` becomes the canonical public base URL for signed export links and must point at the externally reachable download endpoint.

## Test Plan
- Update export download tests so they run with a temp `EXPORT_DIR` and verify the download endpoint serves files from that configured directory, not from a hard-coded path.
- Add a path-safety test for `/exports/download` covering:
  - valid signed path inside export dir -> `200`
  - expired signature -> `403`
  - invalid signature -> `403`
  - path outside export dir -> `403`
  - missing file inside export dir -> `404`
- Add a runtime wiring check for the container setup:
  - worker-written export is visible to API through the shared volume
  - cleanup job removes the file from the shared export volume and the job record from the DB

## Assumptions
- Minimal patch means staying on filesystem-backed exports for now, not moving to S3/GCS.
- The production platform can mount one persistent shared volume into both API and worker; if it cannot, the next step is object storage rather than more filesystem patching.
- Frontend code does not need changes because it already accepts absolute download URLs.
