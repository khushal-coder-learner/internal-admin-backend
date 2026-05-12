# app/storage/base.py

from typing import Protocol
from pathlib import Path

class StorageBackend(Protocol):

    def upload_file(
        self,
        local_path: str,
        object_name: str,
    ) -> str:
        ...

    def generate_download_url(
        self,
        object_name: str,
        expires_in: int = 600,
    ) -> str:
        ...

    def resolve_path(
        self,
        object_name: str | Path,
    ) -> Path:
        ...