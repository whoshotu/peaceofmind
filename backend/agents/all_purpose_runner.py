"""All-Purpose Runner Agent

Implements the function signature declared in QwenClient:

    name: run_external_task
    parameters: {operation: str, payload: object}

Supported operations:
- verify_paypal: payload must contain "order_id"
- send_sms: payload must contain "phone_number" and "message"
- oss_upload: payload must contain "file_name" and "content"

Each operation simply forwards to the corresponding adapter and returns the adapter's result.
"""
import json
from ..adapters.sms_adapter import send_sms
from ..adapters.paypal_adapter import verify_payment
from alibabacloud_oss20190517.client import Client as OssClient
import os

async def run(args: dict) -> dict:
    operation = args.get("operation")
    payload = args.get("payload", {})
    if operation == "verify_paypal":
        order_id = payload.get("order_id")
        success = verify_payment(order_id)
        return {"operation": operation, "verified": success}
    if operation == "send_sms":
        phone = payload.get("phone_number")
        message = payload.get("message")
        result = send_sms(phone, message)
        return {"operation": operation, "result": result}
    if operation == "oss_upload":
        bucket = os.getenv("OSS_BUCKET_NAME")
        endpoint = os.getenv("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
        access_key_id = os.getenv("ALIBABA_ACCESS_KEY_ID")
        access_key_secret = os.getenv("ALIBABA_ACCESS_KEY_SECRET")
        client = OssClient(access_key_id=access_key_id, access_key_secret=access_key_secret, endpoint=endpoint)
        file_name = payload.get("file_name")
        content = payload.get("content", "").encode("utf-8")
        from alibabacloud_oss20190517.models import PutObjectRequest
        req = PutObjectRequest(bucket, file_name, content)
        resp = client.put_object(req)
        return {"operation": operation, "etag": resp.body.etag}
    return {"error": f"Unsupported operation {operation}"}
