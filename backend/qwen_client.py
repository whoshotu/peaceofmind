import os
import json
import logging
from enum import Enum
from typing import Optional, List, Dict, Any
from http import HTTPStatus

import dashscope

logger = logging.getLogger(__name__)


class QwenModel(str, Enum):
    TURBO = "qwen-turbo"
    PLUS = "qwen-plus"
    MAX = "qwen-max"
    LONG = "qwen-long"


AGENT_MODELS: Dict[str, QwenModel] = {
    "manager": QwenModel.MAX,
    "community": QwenModel.TURBO,
    "media": QwenModel.TURBO,
    "schedule": QwenModel.TURBO,
    "payments": QwenModel.PLUS,
    "memory": QwenModel.LONG,
}


class QwenClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        self.base_url = base_url or os.environ.get("DASHSCOPE_BASE_URL")

        self.total_tokens_used = 0
        self.call_count = 0

        if not self.api_key:
            logger.warning("DASHSCOPE_API_KEY not set — running in stub mode.")
            self.stub_mode = True
        else:
            self.stub_mode = False
            dashscope.api_key = self.api_key
            if self.base_url:
                dashscope.base_http_api_url = self.base_url
            logger.info(
                "QwenClient ready via DashScope%s",
                f" → {self.base_url}" if self.base_url else ""
            )

    def chat(
        self,
        messages: List[Dict[str, str]],
        agent_name: str = "manager",
        model: Optional[QwenModel] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        result_format: str = "message",
    ) -> Dict[str, Any]:
        if self.stub_mode:
            return self._stub_response(agent_name)

        selected_model = (model or AGENT_MODELS.get(agent_name, QwenModel.TURBO)).value

        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        try:
            response = dashscope.Generation.call(
                model=selected_model,
                messages=full_messages,
                result_format=result_format,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            if response.status_code != HTTPStatus.OK:
                logger.error("[%s] DashScope error %s: %s", agent_name.upper(), response.status_code, response.message)
                return {
                    "success": False,
                    "content": "",
                    "error": response.message,
                    "status_code": int(response.status_code),
                }

            message = response.output.choices[0].message
            content = message.get("content", "") if isinstance(message, dict) else getattr(message, "content", "")

            usage = getattr(response, "usage", None)
            input_tokens = getattr(usage, "input_tokens", 0) or 0
            output_tokens = getattr(usage, "output_tokens", 0) or 0
            total = input_tokens + output_tokens

            self.total_tokens_used += total
            self.call_count += 1

            logger.info("[%s] ✓ %s | tokens=%s", agent_name.upper(), selected_model, total)

            return {
                "success": True,
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "tokens_used": total,
                "model": selected_model,
            }

        except Exception as e:
            logger.exception("[%s] Unexpected error: %s", agent_name.upper(), e)
            return {"success": False, "content": "", "error": str(e)}

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        agent_name: str = "payments",
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        result = self.chat(
            messages=messages,
            agent_name=agent_name,
            system_prompt=(system_prompt or "") + "\nRespond only with valid JSON.",
            temperature=0.1,
            **kwargs,
        )
        if result.get("success") and result.get("content"):
            try:
                result["parsed"] = json.loads(result["content"])
            except json.JSONDecodeError as e:
                result["parsed"] = None
                result["parse_error"] = str(e)
        return result

    def get_stats(self) -> Dict[str, Any]:
        return {
            "call_count": self.call_count,
            "total_tokens": self.total_tokens_used,
            "avg_tokens_per_call": round(self.total_tokens_used / self.call_count) if self.call_count else 0,
        }

    def _stub_response(self, agent_name: str) -> Dict[str, Any]:
        stubs = {
            "manager": '{"goal_summary":"Process stream","tasks":[]}',
            "community": '{"reply_draft":"Thanks so much! 🙏","priority":"medium","flag":null}',
            "media": '{"renamed":["VOD_2026-07-09_twitch_stream.mp4"],"moved":[],"tags":[],"errors":[]}',
            "schedule": '{"logged":{"stream_id":"S-001","duration_minutes":120},"alerts":[],"missed_streams":[]}',
            "payments": '{"payments":[],"total_outstanding":0.00,"alerts":[]}',
            "memory": '{"operation":"retrieve","results":[],"context_tokens_used":0}',
        }
        return {
            "success": True,
            "content": stubs.get(agent_name, '{}'),
            "input_tokens": 0,
            "output_tokens": 0,
            "tokens_used": 0,
            "model": "stub",
        }


_client: Optional[QwenClient] = None


def get_client() -> QwenClient:
    global _client
    if _client is None:
        _client = QwenClient()
    return _client


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    print("\n=== QwenClient Smoke Test (DashScope SDK) ===\n")

    client = QwenClient()
    result = client.chat(
        messages=[{"role": "user", "content": "Say hello in one sentence and tell me which model you are."}],
        agent_name="manager",
    )

    print(f"success={result.get('success')} | model={result.get('model')} | tokens={result.get('tokens_used')}")
    print(f"response: {result.get('content', '')[:160]}")
    print(f"\nstats: {json.dumps(client.get_stats(), indent=2)}")
