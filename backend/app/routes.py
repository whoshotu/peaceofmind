from fastapi import APIRouter, Body
from ..qwen_client import QwenClient
from ..app.memory import MemoryStore

router = APIRouter()

@router.post("/chat")
async def chat(payload: dict = Body(...)):
    """Receive a user message, forward to Qwen, and return the response."""
    client = QwenClient()
    response = await client.process(payload)
    return response

@router.get("/admin/pending")
def get_pending_tasks():
    """Return a list of tasks awaiting human approval (placeholder)."""
    # In a real implementation this would query Redis/Temporal for pending signals.
    return {"pending": []}
