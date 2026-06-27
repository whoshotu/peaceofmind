import os
from alibabacloud_oss20190517.client import Client as OssClient
from alibabacloud_oss20190517.models import PutObjectRequest

def upload_log(file_name: str, content: str) -> dict:
    """Upload a tiny log file to the OSS bucket defined by env vars.
    Used as proof of Alibaba Cloud usage.
    """
    access_key_id = os.getenv("ALIBABA_ACCESS_KEY_ID")
    access_key_secret = os.getenv("ALIBABA_ACCESS_KEY_SECRET")
    bucket_name = os.getenv("OSS_BUCKET_NAME")
    endpoint = os.getenv("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
    client = OssClient(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        endpoint=endpoint,
    )
    put_req = PutObjectRequest(bucket_name, file_name, content.encode("utf-8"))
    resp = client.put_object(put_req)
    return {"request_id": resp.body.request_id, "etag": resp.body.etag}

def send_sms(phone_number: str, message: str) -> dict:
    """Send an SMS via Alibaba Cloud SMS service (placeholder implementation).
    In a real deployment you would use the Dysmsapi SDK; here we just log to OSS.
    """
    # Log the SMS payload to OSS as proof of usage.
    log_content = f"SMS to {phone_number}: {message}\n"
    return upload_log("sms_log.txt", log_content)
