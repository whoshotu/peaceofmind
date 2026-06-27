import os, requests

def _get_access_token():
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
    auth = (client_id, client_secret)
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    resp = requests.post("https://api.sandbox.paypal.com/v1/oauth2/token", auth=auth, headers=headers, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]

def verify_payment(order_id: str) -> bool:
    """Verify a PayPal order in the sandbox environment.
    Returns True if the order status is COMPLETED.
    """
    token = _get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data.get("status") == "COMPLETED"
