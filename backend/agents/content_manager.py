"""Content Manager Agent

Implements the function signature declared in QwenClient:

    name: manage_content
    parameters: {action: str, title?: str, schedule_time?: str}

Provides very simple placeholder behavior.
"""
import json

async def run(args: dict) -> dict:
    action = args.get("action", "list")
    if action == "create":
        title = args.get("title", "Untitled")
        return {"response": f"Draft '{title}' created.", "confidence": 0.9}
    if action == "schedule":
        title = args.get("title", "Untitled")
        schedule = args.get("schedule_time", "unspecified")
        return {"response": f"'{title}' scheduled for {schedule}.", "confidence": 0.9}
    # default list action
    return {"response": "Listing all drafts (placeholder).", "confidence": 0.8}
