import os
from fastapi import FastAPI
from .routes import router

app = FastAPI(title="peaceofmind Backend")
app.include_router(router)
