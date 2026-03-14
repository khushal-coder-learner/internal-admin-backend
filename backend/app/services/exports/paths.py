import os
from pathlib import Path


def get_export_dir() -> Path:
    export_dir = Path(os.getenv("EXPORT_DIR", "storage/exports"))
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir

