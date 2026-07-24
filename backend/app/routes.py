from fastapi import APIRouter, Body, HTTPException

from qwen_client import get_client

router = APIRouter()


@router.get("/health/live")
def liveness():
    return {"status": "ok"}


@router.get("/health/ready")
def readiness():
    return {"status": "ok"}


@router.post("/chat")
async def chat(payload: dict = Body(...)):
    """Receive messages, forward them to Qwen, and return its response."""
    messages = payload.get("messages")

    if not isinstance(messages, list) or not messages:
        user_message = payload.get("message") or payload.get("content")

        if not isinstance(user_message, str) or not user_message.strip():
            raise HTTPException(
                status_code=422,
                detail=(
                    "Request body must include a non-empty messages array "
                    "or a non-empty message/content string."
                ),
            )

        messages = [{"role": "user", "content": user_message}]

    if not all(
        isinstance(message, dict)
        and isinstance(message.get("role"), str)
        and isinstance(message.get("content"), str)
        and message["content"].strip()
        for message in messages
    ):
        raise HTTPException(
            status_code=422,
            detail="Each message must contain non-empty role and content strings.",
        )

    system_prompt = payload.get(
        "system_prompt",
        "You are a helpful assistant for content creators. Be concise and practical.",
    )
    agent_name = payload.get("agent_name", "manager")

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
    """Return tasks awaiting human approval."""
    return {"pending": []}
