import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "video/mp4": "mp4",
    "video/webm": "webm",
    "video/quicktime": "mov",
}

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload")
async def upload_media(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {', '.join(ALLOWED_TYPES)}",
        )

    ext = ALLOWED_TYPES[file.content_type]
    media_id = uuid.uuid4().hex[:12]
    filename = f"{media_id}.{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "id": media_id,
        "filename": file.filename or filename,
        "url": f"/uploads/{filename}",
        "type": file.content_type,
        "size": filepath.stat().st_size,
    }


@router.get("")
def list_media(q: str = ""):
    files = []
    for p in sorted(UPLOAD_DIR.iterdir(), key=os.path.getmtime, reverse=True):
        if not p.is_file():
            continue
        if q and q.lower() not in p.name.lower():
            continue
        ext = p.suffix.lstrip(".")
        kind = "image" if ext in ("jpg", "jpeg", "png", "gif", "webp") else "video"
        files.append({
            "id": p.stem,
            "filename": p.name,
            "url": f"/uploads/{p.name}",
            "type": kind,
            "size": p.stat().st_size,
        })
    return {"files": files}


@router.delete("/{media_id}")
def delete_media(media_id: str):
    for p in UPLOAD_DIR.iterdir():
        if p.is_file() and p.stem == media_id:
            p.unlink()
            return {"deleted": media_id}
    raise HTTPException(status_code=404, detail="File not found")
