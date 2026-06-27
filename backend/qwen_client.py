import os
import json
from qwencloud import QwenClient as QwenSDK

class QwenClient:
    def __init__(self):
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            raise EnvironmentError("QWEN_API_KEY not set")
        self.client = QwenSDK(api_key=api_key)
        # Define the function signatures that agents expose to Qwen
        self.functions = [
            {
                "name": "handle_customer_query",
                "description": "Answer a viewer/customer question, possibly delegating to other agents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "The user question"},
                        "user_id": {"type": "string", "description": "Identifier of the user"}
                    },
                    "required": ["question", "user_id"]
                }
            },
            {
                "name": "manage_content",
                "description": "Create, schedule or organize content drafts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["create", "schedule", "list"], "description": "What to do with the content"},
                        "title": {"type": "string", "description": "Title of the draft"},
                        "schedule_time": {"type": "string", "format": "date-time", "description": "When to publish"}
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "assist_creator",
                "description": "Daily assistance tasks such as reminders, calendar sync, idea suggestions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Description of the assistance task"}
                    },
                    "required": ["task"]
                }
            },
            {
                "name": "run_external_task",
                "description": "Execute an external operation like PayPal verification or sending SMS.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["verify_paypal", "send_sms", "oss_upload"], "description": "External operation to perform"},
                        "payload": {"type": "object", "description": "Arbitrary payload for the operation"}
                    },
                    "required": ["operation", "payload"]
                }
            }
        ]

    async def process(self, payload: dict) -> dict:
        """Send the user payload to Qwen Cloud with function definitions.
        The response may contain a `function_call` field indicating which agent to invoke.
        """
        # Simple wrapper – in real usage you would handle async properly.
        response = self.client.chat_completion(
            model="qwen-max",
            messages=[{"role": "user", "content": json.dumps(payload)}],
            functions=self.functions,
            temperature=0.2,
        )
        # Return the raw response for the orchestrator to interpret.
        return response.to_dict()
