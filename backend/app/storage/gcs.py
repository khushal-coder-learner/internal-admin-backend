# app/storage/gcs.py

from google.cloud import storage


class GCSStorageBackend:

    def __init__(self):

        self.client = storage.Client()

        self.bucket = self.client.bucket(
            "internal-admin-exports"
        )

    def upload_file(
        self,
        local_path: str,
        object_name: str,
    ):

        blob = self.bucket.blob(object_name)

        blob.upload_from_filename(local_path)

        return object_name

    def generate_download_url(
        self,
        object_name: str,
        expires_in: int = 600,
    ):

        blob = self.bucket.blob(object_name)

        return blob.generate_signed_url(
            version="v4",
            expiration=expires_in,
            method="GET",
        )
    
    def resolve_path(
        self,
        object_name,
    ):
        raise NotImplementedError