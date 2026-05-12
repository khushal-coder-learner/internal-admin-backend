# app/storage/__init__.py

from app.core.config import settings

if settings.storage_backend == "gcs":
    from app.storage.gcs import GCSStorageBackend

    storage = GCSStorageBackend()

else:
    from app.storage.local import LocalStorageBackend

    storage = LocalStorageBackend()