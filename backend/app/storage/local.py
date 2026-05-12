# app/storage/local.py
import time
import hmac
import hashlib
from pathlib import Path
from fastapi import Request
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from app.core.config import settings
from app.services.exports.paths import get_export_dir


class LocalStorageBackend:

    def upload_file(self, local_path: str, object_name: str):

        export_dir = get_export_dir()

        final_path = export_dir / object_name

        final_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        Path(local_path).replace(final_path)

        return str(final_path)

    def generate_download_url(
        self,
        file_path: str,
        expires_in: int = 600,
        request: Request | None = None,
    ):
        expiry = int(time.time()) + expires_in

        message = f"{file_path}:{expiry}".encode()

        signature = hmac.new(
            settings.secret_key.encode(),
            message,
            hashlib.sha256
        ).hexdigest()

        params = {
            "path": file_path,
            "expires": expiry,
            "sig": signature
        }

        if request is not None:
            base_url = urlsplit(str(request.url_for("download_export")))
        elif settings.exports_download_url:
            base_url = urlsplit(settings.exports_download_url)
        else:
            base_url = urlsplit("/exports/download")

        query = dict(parse_qsl(base_url.query, keep_blank_values=True))
        query.update(params)

        return urlunsplit(
            (
                base_url.scheme,
                base_url.netloc,
                base_url.path,
                urlencode(query),
                base_url.fragment,
            )
        )

    def resolve_path(
        self,
        object_name: str | Path,
    ) -> Path:

        export_dir = get_export_dir()

        final_path = export_dir / object_name

        return final_path.resolve()