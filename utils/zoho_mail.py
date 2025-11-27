# utils/zoho_mail.py
import requests
from django.conf import settings

def get_zoho_access_token():
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": settings.ZOHO_CLIENT_ID,
        "client_secret": settings.ZOHO_CLIENT_SECRET,
        "refresh_token": settings.ZOHO_REFRESH_TOKEN,
    }
    r = requests.post(url, data=data, timeout=10)
    r.raise_for_status()
    js = r.json()
    return js["access_token"]

def send_zoho_email(to_email, subject, html_content=None, plain_text=None):
    access_token = get_zoho_access_token()
    url = url = "https://mail.zoho.eu/api/sendmail"

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    # Zoho supports form encoded fields for simple sends
    payload = {
        "from": settings.ZOHO_FROM_EMAIL,
        "to": to_email if isinstance(to_email, str) else ",".join(to_email),
        "subject": subject,
        "content": plain_text or "",
    }
    if html_content:
        payload["content"] = html_content

    resp = requests.post(url, data=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()
