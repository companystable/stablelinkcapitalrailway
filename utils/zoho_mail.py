import os
import requests
from django.conf import settings



# ----------------------------
# Get Zoho OAuth access token
# ----------------------------
def get_zoho_access_token():
    """
    Obtain a new access token using the refresh token.
    """
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "refresh_token": ZOHO_REFRESH_TOKEN,
    }

    response = requests.post(url, data=data, timeout=10)
    response.raise_for_status()
    token_data = response.json()

    if "access_token" not in token_data:
        raise Exception(f"Zoho did not return access_token. Response: {token_data}")

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
    accounts_url = "https://mail.zoho.com/api/accounts"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    acc_response = requests.get(accounts_url, headers=headers, timeout=10)
    acc_response.raise_for_status()

    accounts_data = acc_response.json()
    if not accounts_data.get("data"):
        raise Exception("No Zoho mail accounts found for this access token.")

    account_id = accounts_data["data"][0]["accountId"]

    # Step 2: Prepare send email URL
    send_url = f"https://mail.zoho.com/api/accounts/{account_id}/messages?action=send"

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
    response = requests.post(send_url, json=payload, headers=email_headers, timeout=10)
    response.raise_for_status()
    return response.json()

# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    try:
        result = send_zoho_email(
            to_email="recipient@example.com",
            subject="Test Email from Django Zoho API",
            html_content="<h1>Hello from Zoho!</h1>"
        )
        print("Email sent successfully:", result)
    except Exception as e:
        print("Error sending Zoho email:", e)
