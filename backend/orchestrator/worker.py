from datetime import timedelta
from typing import Any

from temporalio import activity, workflow

from ..agents.all_purpose_runner import run as ar_run
from ..agents.content_manager import run as cm_run
from ..agents.creator_assistant import run as ca_run
from ..agents.customer_service import run as cs_run


@activity.defn
async def invoke_agent(name: str, args: dict) -> dict:
    """Invoke one registered specialist agent."""
    if name == "handle_customer_query":
        return await cs_run(args)
    if name == "manage_content":
        return await cm_run(args)
    if name == "assist_creator":
        return await ca_run(args)
    if name == "run_external_task":
        return await ar_run(args)
    return {"error": f"Unknown agent function: {name}"}


@activity.defn
async def qwen_process(payload: dict) -> dict:
    """Use the SDK-only Qwen client to select a specialist agent."""
    from ..qwen_client import get_client

    system_prompt = """
You are the routing manager for a creator-support multi-agent system.

Choose the single best action for the incoming request:
- handle_customer_query: follower questions, DMs, support, community replies
- manage_content: media files, content organization, tagging, publishing workflow
- assist_creator: creator planning, schedules, stream tracking, creative support
- run_external_task: other operational tasks that require an outside tool

Return JSON only with this exact shape:
{
  "function_call": {
    "name": "one_allowed_action",
    "arguments": {}
  }
}

If you cannot safely select an action, return:
{"function_call": null, "content": "brief explanation"}
""".strip()

    user_request = (
        payload.get("message")
        or payload.get("content")
        or payload.get("task")
        or str(payload)
    )

    result = get_client().chat_json(
        messages=[{"role": "user", "content": str(user_request)}],
        agent_name="manager",
        system_prompt=system_prompt,
    )

    if not result.get("success"):
        return {
            "function_call": None,
            "content": "Unable to route the request.",
            "error": result.get("error", "Qwen request failed."),
        }

    parsed = result.get("parsed")
    if not isinstance(parsed, dict):
        return {
            "function_call": None,
            "content": result.get("content", "Unable to parse routing response."),
        }

    return parsed


@workflow.defn
class MainWorkflow:
    @workflow.run
    async def run(self, payload: dict) -> dict | str:
        qwen_resp = await workflow.execute_activity(
            qwen_process,
            payload,
            start_to_close_timeout=timedelta(seconds=30),
        )

        function_call = qwen_resp.get("function_call")
        if not isinstance(function_call, dict):
            return qwen_resp.get("content", "No agent action selected.")

        name = function_call.get("name")
        arguments: Any = function_call.get("arguments", {})
        if not isinstance(arguments, dict):
            arguments = {}

        return await workflow.execute_activity(
            invoke_agent,
            name,
            arguments,
            start_to_close_timeout=timedelta(seconds=60),
        )
