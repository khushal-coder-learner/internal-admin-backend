from app.services.exports import EXPORT_GENERATORS, get_export_total_rows
from sqlalchemy.orm.attributes import flag_modified

async def execute_export(db, redis, job):

    payload = job.payload or {}
    export_type = payload["export_type"]

    generator = EXPORT_GENERATORS.get(export_type)

    if not generator:
        raise ValueError(f"Unknown export type: {export_type}")
    
    total_rows = get_export_total_rows(db, export_type)

    job.payload = {
        **payload,
        "progress": 0 if total_rows > 0 else 100,
        "total_rows": total_rows,
        "rows_processed": 0,
    }
    flag_modified(job, "payload")
    db.commit()

    COMMIT_EVERY_ROWS = 500
    last_committed_rows = 0

    def progress_update(rows_written: int):

        nonlocal last_committed_rows

        job.payload["rows_processed"] = int(rows_written)
        if total_rows > 0:
            job.payload["progress"] = min(
                100,
                int((rows_written / total_rows) * 100),
            )
        else:
            job.payload["progress"] = 100
        flag_modified(job, "payload")

        if (
            rows_written == total_rows
            or last_committed_rows == 0
            or (rows_written - last_committed_rows) >= COMMIT_EVERY_ROWS
        ):
            db.commit()
            last_committed_rows = rows_written

    file_path = generator(db, progress_callback=progress_update)

    job.payload = {
        **job.payload,
        "file_path": file_path,
        "progress": 100
    }
    flag_modified(job, "payload")
    db.commit()
