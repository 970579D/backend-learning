from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

UPLOAD_DIR = Path("uploads/avatars")
MAX_BYTES = 5 * 1024 * 1024


def save_avatar(file: UploadFile) -> str:
    """Validate, resize and write a JPG. Returns the file name."""
    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Image must be smaller than 5 MB")

    try:
        img = Image.open(BytesIO(data))
        img.load()                       # forces a full decode, so broken files fail here
    except (UnidentifiedImageError, OSError):
        raise ValueError("File is not a valid image")

    img = img.convert("RGB")             # JPEG has no alpha channel
    img.thumbnail((512, 512))            # keeps the ratio, never enlarges

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{uuid4().hex}.jpg"          # random name: no user input in the path
    img.save(UPLOAD_DIR / name, "JPEG", quality=85)
    return name


def delete_avatar(name: str | None) -> None:
    if name:
        (UPLOAD_DIR / Path(name).name).unlink(missing_ok=True)   # .name strips any folder part