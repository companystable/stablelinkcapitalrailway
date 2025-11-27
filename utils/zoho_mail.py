import os
import requests
from django.conf import settings

ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
ZOHO_FROM_EMAIL = os.getenv("ZOHO_FROM_EMAIL", "support@stablelinkcapital.com")

ZOHO_OAUTH_URL = "https://accounts.zoho.com/oauth/v2/token"
ZOHO_MAIL_BASE_URL = "https://mail.zoho.com/api"

def get_zoho_access_token():
    data = {
        "grant_type": "refresh_token",
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "refresh_token": ZOHO_REFRESH_TOKEN,
    }
    response = requests.post(ZOHO_OAUTH_URL, data=data, timeout=10)
    token_data = response.json()
    if "access_token" not in token_data:
        raise Exception(f"No access_token returned. Response: {token_data}")
    return token_data["access_token"]

def send_zoho_email(to_email, subject, html_content=None, plain_text=None):
    access_token = get_zoho_access_token()
    accounts_url = f"{ZOHO_MAIL_BASE_URL}/accounts"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    accounts_data = requests.get(accounts_url, headers=headers, timeout=10).json()
    if not accounts_data.get("data"):
        raise Exception("No Zoho accounts found.")
    account_id = accounts_data["data"][0]["accountId"]

    send_url = f"{ZOHO_MAIL_BASE_URL}/accounts/{account_id}/messages?action=send"
    payload = {
        "fromAddress": ZOHO_FROM_EMAIL,
        "toAddress": [to_email] if isinstance(to_email, str) else to_email,
        "subject": subject,
        "content": plain_text or "",
    }
    if html_content:
        payload["content"] = html_content
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}", "Content-Type": "application/json"}
    response = requests.post(send_url, json=payload, headers=headers, timeout=10)
    return response.json()
