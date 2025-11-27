import requests
from django.conf import settings

def get_zoho_access_token():
    """
    Retrieve a Zoho access token using a refresh token.
    Returns the access token and api_domain.
    """
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

    if "access_token" not in js or "api_domain" not in js:
        raise Exception(f"Zoho did not return access_token or api_domain. Response: {js}")

    return js["access_token"], js["api_domain"]  # Return domain for correct region

def send_zoho_email(to_email, subject, html_content=None, plain_text=None):
    """
    Sends an email via Zoho Mail using the proper API domain and accountId.
    """
    access_token, api_domain = get_zoho_access_token()

    # Step 1: Get accountId
    accounts_url = f"{api_domain}/mail/v1/accounts"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    acc_response = requests.get(accounts_url, headers=headers, timeout=10)
    acc_response.raise_for_status()
    account_id = acc_response.json()["data"][0]["accountId"]

    # Step 2: Send email
    send_url = f"{api_domain}/mail/v1/accounts/{account_id}/messages"

    payload = {
        "fromAddress": settings.ZOHO_FROM_EMAIL,
        "toAddress": to_email if isinstance(to_email, list) else [to_email],
        "subject": subject,
        "content": html_content or plain_text or "",
    }

    email_headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    resp = requests.post(send_url, json=payload, headers=email_headers, timeout=10)
    resp.raise_for_status()
    return resp.json()
