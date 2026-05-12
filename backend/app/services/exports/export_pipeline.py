import tempfile
from pathlib import Path
from uuid import uuid4

from app.storage import storage
from .csv_writer import write_csv_paged


def generate_csv_export(
    *,
    filename_prefix: str,
    headers,
    fetch_page,
    progress_callback=None,
):

    object_name = (
        f"exports/{filename_prefix}_{uuid4()}.csv"
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_path = (
            Path(temp_dir) / f"{filename_prefix}.csv"
        )

        write_csv_paged(
            temp_path,
            headers,
            fetch_page,
            progress_callback=progress_callback,
            progress_step=100,
            page_size=1000,
        )

        storage.upload_file(
            str(temp_path),
            object_name,
        )

    return object_name