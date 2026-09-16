"""Image uploads for the admin panel — staff pick a file instead of pasting a URL.

Saved under ``settings.upload_dir`` (mounted at ``/uploads`` by app.main) and
returned as an absolute URL so it renders the same from the admin, SSR pages
and the browser regardless of which origin is loading them.
"""
import mimetypes
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.deps import StaffUser

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/svg+xml"}
EXT_FIXUPS = {".jpe": ".jpg", ".jfif": ".jpg"}


def _upload_dir() -> Path:
    path = Path(settings.upload_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile, _: StaffUser) -> dict:
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Разрешены только изображения: JPEG, PNG, WEBP, GIF, SVG",
        )
    data = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Файл больше {settings.max_upload_mb} МБ")
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Пустой файл")

    ext = mimetypes.guess_extension(content_type) or Path(file.filename or "").suffix or ".bin"
    ext = EXT_FIXUPS.get(ext, ext)
    name = f"{uuid.uuid4().hex}{ext}"
    (_upload_dir() / name).write_bytes(data)

    return {"url": f"{settings.public_base_url.rstrip('/')}/uploads/{name}"}
