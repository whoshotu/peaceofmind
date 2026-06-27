import os
from temporalio import workflow, activity
from datetime import timedelta

# Import agent run functions
from ..agents.customer_service import run as cs_run
from ..agents.content_manager import run as cm_run
from ..agents.creator_assistant import run as ca_run
from ..agents.all_purpose_runner import run as ar_run

# Activity wrappers (Temporal activities must be async functions)
@activity.defn
async def invoke_agent(name: str, args: dict) -> dict:
    if name == "handle_customer_query":
        return await cs_run(args)
    if name == "manage_content":
        return await cm_run(args)
    if name == "assist_creator":
        return await ca_run(args)
    if name == "run_external_task":
        return await ar_run(args)
    return {"error": f"Unknown agent function {name}"}

@activity.defn
async def qwen_process(payload: dict) -> dict:
    from ..qwen_client import QwenClient
    client = QwenClient()
    return await client.process(payload)

@workflow.defn
class MainWorkflow:
    @workflow.run
    async def run(self, payload: dict) -> dict:
        # Call Qwen to decide which function to invoke
        qwen_resp = await workflow.execute_activity(
            qwen_process,
            payload,
            start_to_close_timeout=timedelta(seconds=30),
        )
        function_call = qwen_resp.get("function_call")
        if not function_call:
            # No function selected – just return content
            return qwen_resp.get("content", "")
        name = function_call.get("name")
        arguments = function_call.get("arguments", {})
        # Invoke the appropriate agent activity
        result = await workflow.execute_activity(
            invoke_agent,
            name,
            arguments,
            start_to_close_timeout=timedelta(seconds=60),
        )
        return result
