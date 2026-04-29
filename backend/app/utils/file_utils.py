import hmac
import hashlib
import time
from urllib.parse import urlencode
from app.core.config import settings

from fastapi import Request

def generate_signed_download_url(
    request: Request,
    file_path: str,
    expires_in: int = 600
):
    expiry = int(time.time()) + expires_in

    message = f"{file_path}:{expiry}".encode()

    signature = hmac.new(
        settings.secret_key.encode(),
        message,
        hashlib.sha256
    ).hexdigest()

    params = urlencode({
        "path": file_path,
        "expires": expiry,
        "sig": signature
    })

    base_url = request.url_for("download_export")

    return f"{base_url}?{params}"