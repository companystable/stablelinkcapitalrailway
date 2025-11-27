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
    if "access_token" not in js:
        raise Exception(f"Zoho did not return access_token. Response: {js}")
    return js["access_token"], js["api_domain"]  # get the domain from token response

def send_zoho_email(to_email, subject, html_content=None, plain_text=None):
    access_token, api_domain = get_zoho_access_token()

    # Step 1: Get accountId
    accounts_url = f"{api_domain}/mail/v1/accounts"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    acc_response = requests.get(accounts_url, headers=headers, timeout=10)
    acc_response.raise_for_status()
    account_id = acc_response.json()["data"][0]["accountId"]

    # Step 2: Send email using accountId
    send_url = f"{api_domain}/mail/v1/accounts/{account_id}/messages"

    payload = {
        "fromAddress": settings.ZOHO_FROM_EMAIL,
        "toAddress": to_email if isinstance(to_email, list) else [to_email],
        "subject": subject,
        "content": plain_text or "",
        "contentType": "html" if html_content else "text/plain"
    }

    if html_content:
        payload["content"] = html_content

    email_headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    resp = requests.post(send_url, json=payload, headers=email_headers, timeout=10)
    resp.raise_for_status()
    return resp.json()
