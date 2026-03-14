from app.services.exports import EXPORT_GENERATORS
from sqlalchemy.orm.attributes import flag_modified

async def execute_export(db, redis, job):

    export_type = job.payload["export_type"]

    generator = EXPORT_GENERATORS.get(export_type)

    if not generator:
        raise ValueError(f"Unknown export type: {export_type}")
    
    processed_rows = 0

    def progress_update(rows_written):

        nonlocal processed_rows

        processed_rows = rows_written

        job.payload["rows_processed"] = rows_written
        flag_modified(job, "payload")

        db.flush()

    file_path = generator(db, progress_callback= progress_update)

    job.payload = {
        **job.payload, 
        "file_path": file_path,
        "progress": 100
    }
