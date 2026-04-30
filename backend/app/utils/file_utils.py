import hmac
import hashlib
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from app.core.config import settings

def generate_signed_download_url(
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

    params = {
        "path": file_path,
        "expires": expiry,
        "sig": signature
    }

    base_url = urlsplit(settings.exports_download_url)
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
