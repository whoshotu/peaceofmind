import uuid
from fastapi import APIRouter, Body, HTTPException
from qwen_client import get_client

router = APIRouter(prefix="/fans", tags=["fans"])

profiles: dict = {}
history: dict = {}


@router.get("")
def list_fans():
    return {"fans": list(profiles.values())}


@router.post("")
def create_fan(payload: dict = Body(...)):
    fan_id = uuid.uuid4().hex[:8]
    profile = {
        "id": fan_id,
        "name": payload.get("name", "Anonymous"),
        "tier": payload.get("tier", "free"),
        "notes": payload.get("notes", ""),
    }
    profiles[fan_id] = profile
    history[fan_id] = []
    return profile


@router.get("/{fan_id}")
def get_fan(fan_id: str):
    p = profiles.get(fan_id)
    if not p:
        raise HTTPException(404, "Fan not found")
    return p


@router.post("/{fan_id}/chat")
async def fan_chat(fan_id: str, payload: dict = Body(...)):
    p = profiles.get(fan_id)
    if not p:
        raise HTTPException(404, "Fan not found")

    user_message = payload.get("message") or payload.get("content")
    if not user_message or not user_message.strip():
        raise HTTPException(422, "message is required")

    tier_desc = {
        "free": "a free-tier follower",
        "basic": "a basic subscriber",
        "premium": "a premium subscriber",
        "vip": "a VIP subscriber",
    }.get(p["tier"], "a subscriber")

    system_prompt = (
        f"You are a friendly community manager for a content creator. "
        f"You are speaking to {p['name']}, {tier_desc}. "
        f"Be warm and helpful. Fan notes: {p['notes']}. "
        f"Respond in a way that makes {p['name']} feel valued."
    )

    h = history.setdefault(fan_id, [])
    h.append({"role": "user", "content": user_message})

    result = get_client().chat(
        messages=h[-10:],
        agent_name="community",
        system_prompt=system_prompt,
    )

    if not result.get("success"):
        reply = f"Hey {p['name']}! Thanks for reaching out. I'll make sure the creator sees your message. 😊"
    else:
        reply = result.get("content", "")
    h.append({"role": "assistant", "content": reply})

    return {
        "content": reply,
        "fan_id": fan_id,
        "fan_name": p["name"],
        "model": result.get("model"),
        "tokens_used": result.get("tokens_used"),
    }


@router.get("/{fan_id}/history")
def get_fan_history(fan_id: str):
    h = history.get(fan_id)
    if h is None:
        raise HTTPException(404, "Fan not found")
    return {"history": h}
