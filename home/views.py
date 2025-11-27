from django.shortcuts import render

def home_view(request):
    return render(request, 'home/index.html')


from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings

from django.http import HttpResponse
from utils.zoho_mail import send_zoho_email
import logging

logger = logging.getLogger(__name__)

def test_email(request):
    try:
        result = send_zoho_email(
            to_email="vanessavaldezwhite@gmail.com",
            subject="Zoho API Test",
            html_content="<strong>Zoho is working</strong>",
            plain_text="Zoho is working"
        )

        # Log success to Railway logs
        logger.info(f"Zoho email sent successfully: {result}")

        return HttpResponse(f"Zoho API email sent successfully! Response: {result}")

    except Exception as e:
        # Log error to Railway logs
        logger.error(f"Zoho email error: {e}")

        return HttpResponse(f"Error sending Zoho email: {e}")



import requests
from django.conf import settings
from django.http import HttpResponse

def zoho_oauth_callback(request):
    code = request.GET.get('code')
    if not code:
        return HttpResponse("Missing code in querystring. Use the Zoho auth URL to authorize.")

    token_url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.ZOHO_CLIENT_ID,
        "client_secret": settings.ZOHO_CLIENT_SECRET,
        "redirect_uri": "https://stablelinkcapital.com/zoho/oauth/callback/",
        "code": code,
    }
    resp = requests.post(token_url, data=data)
    if resp.status_code != 200:
        return HttpResponse(f"Token exchange failed: {resp.status_code} {resp.text}", status=500)

    payload = resp.json()
    # payload contains access_token, refresh_token
    refresh_token = payload.get("refresh_token")
    return HttpResponse(f"REFRESH_TOKEN: {refresh_token}\n\nPaste that into Railway as ZOHO_REFRESH_TOKEN")
