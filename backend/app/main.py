import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import router
from .media_routes import router as media_router
from .fans_routes import router as fans_router

UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="peaceofmind Backend")
app.include_router(router)
app.include_router(media_router)
app.include_router(fans_router)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
