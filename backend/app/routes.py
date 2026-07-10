from fastapi import APIRouter, Body, HTTPException

from ..qwen_client import get_client
from ..app.memory import MemoryStore

router = APIRouter()


@router.post("/chat")
async def chat(payload: dict = Body(...)):
    """Receive a user message, forward it to Qwen, and return its response."""
    user_message = payload.get("message") or payload.get("content")
    if not isinstance(user_message, str) or not user_message.strip():
        raise HTTPException(
            status_code=422,
            detail="Request body must include a non-empty 'message' or 'content' string.",
        )

    system_prompt = payload.get(
        "system_prompt",
        "You are a helpful assistant for content creators. Be concise and practical.",
    )
    agent_name = payload.get("agent_name", "manager")

    messages = payload.get("messages")
    if not isinstance(messages, list):
        messages = [{"role": "user", "content": user_message}]

    result = get_client().chat(
        messages=messages,
        agent_name=agent_name,
        system_prompt=system_prompt,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=502,
            detail=result.get("error", "Qwen request failed."),
        )

    return {
        "content": result["content"],
        "model": result["model"],
        "tokens_used": result["tokens_used"],
    }


@router.get("/admin/pending")
def get_pending_tasks():
    """Return a list of tasks awaiting human approval (placeholder)."""
    return {"pending": []}
