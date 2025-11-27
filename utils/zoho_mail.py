import os
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# ----------------------------
# Fetch Zoho credentials
# ----------------------------
ZOHO_CLIENT_ID = getattr(settings, "ZOHO_CLIENT_ID", os.getenv("ZOHO_CLIENT_ID"))
ZOHO_CLIENT_SECRET = getattr(settings, "ZOHO_CLIENT_SECRET", os.getenv("ZOHO_CLIENT_SECRET"))
ZOHO_REFRESH_TOKEN = getattr(settings, "ZOHO_REFRESH_TOKEN", os.getenv("ZOHO_REFRESH_TOKEN"))
ZOHO_FROM_EMAIL = getattr(settings, "ZOHO_FROM_EMAIL", os.getenv("ZOHO_FROM_EMAIL", "support@stablelinkcapital.com"))

# ----------------------------
# Zoho API endpoints (pick one)
# ----------------------------
# For EU region:
# ZOHO_OAUTH_URL = "https://accounts.zoho.eu/oauth/v2/token"
# ZOHO_MAIL_BASE_URL = "https://mail.zoho.eu/api"

# For global/com region:
ZOHO_OAUTH_URL = "https://accounts.zoho.com/oauth/v2/token"
ZOHO_MAIL_BASE_URL = "https://mail.zoho.com/api"

# ----------------------------
# Get Zoho OAuth access token
# ----------------------------
def get_zoho_access_token():
    """
    Obtain a new access token using the refresh token.
    """
    data = {
        "grant_type": "refresh_token",
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "refresh_token": ZOHO_REFRESH_TOKEN,
    }

    try:
        response = requests.post(ZOHO_OAUTH_URL, data=data, timeout=10)
        token_data = response.json()
        logger.info(f"Zoho token response: {token_data}")
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching Zoho access token: {e}")
        raise Exception(f"Error fetching Zoho access token: {e}")

    if "access_token" not in token_data:
        raise Exception(f"No access_token returned by Zoho. Response: {token_data}")

    return token_data["access_token"]

# ----------------------------
# Send email via Zoho Mail API v2
# ----------------------------
def send_zoho_email(to_email, subject, html_content=None, plain_text=None):
    """
    Sends an email using Zoho Mail API v2.
    """
    access_token = get_zoho_access_token()

    # Step 1: Get accountId
    accounts_url = f"{ZOHO_MAIL_BASE_URL}/accounts"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

    try:
        acc_response = requests.get(accounts_url, headers=headers, timeout=10)
        accounts_data = acc_response.json()
        logger.info(f"Zoho accounts response: {accounts_data}")
        acc_response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching Zoho account ID: {e}")
        raise Exception(f"Error fetching Zoho account ID: {e}")

    if not accounts_data.get("data"):
        raise Exception(f"No Zoho mail accounts found for this access token. Response: {accounts_data}")

    account_id = accounts_data["data"][0]["accountId"]

    # Step 2: Prepare send email URL
    send_url = f"{ZOHO_MAIL_BASE_URL}/accounts/{account_id}/messages?action=send"

    # Step 3: Prepare payload
    payload = {
        "fromAddress": ZOHO_FROM_EMAIL,
        "toAddress": [to_email] if isinstance(to_email, str) else to_email,
        "subject": subject,
        "content": plain_text or "",
    }

    if html_content:
        payload["content"] = html_content

    # Step 4: Set headers
    email_headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    # Step 5: Send email
    try:
        response = requests.post(send_url, json=payload, headers=email_headers, timeout=10)
        result = response.json()
        logger.info(f"Zoho email send response: {result}")
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error sending Zoho email: {e}")
        raise Exception(f"Error sending Zoho email: {e}")

    return result

# ----------------------------
# Example usage (local testing)
# ----------------------------
if __name__ == "__main__":
    try:
        result = send_zoho_email(
            to_email="vanessavaldezwhite@gmail.com",
            subject="Test Email from Django Zoho API",
            html_content="<h1>Hello from Zoho!</h1>"
        )
        print("Email sent successfully:", result)
    except Exception as e:
        print("Error sending Zoho email:", e)
