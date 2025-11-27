from django.shortcuts import render

def home_view(request):
    return render(request, 'home/index.html')

import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from utils.zoho_mail import send_zoho_email

logger = logging.getLogger(__name__)


def test_email(request):
    """
    Test endpoint to send a Zoho email.
    """
    try:
        result = send_zoho_email(
            to_email="vanessavaldezwhite@gmail.com",
            subject="Zoho API Test",
            html_content="<strong>Zoho is working</strong>",
            plain_text="Zoho is working"
        )

        logger.info(f"Zoho email sent successfully: {result}")
        return JsonResponse({
            "status": "success",
            "message": "Zoho API email sent successfully",
            "response": result
        })

    except Exception as e:
        logger.error(f"Zoho email error: {e}")
        return JsonResponse({
            "status": "error",
            "message": f"Error sending Zoho email: {e}"
        }, status=500)


@csrf_exempt
def zoho_oauth_callback(request):
    """
    OAuth callback endpoint for Zoho Mail.
    Expects ?code= query parameter from Zoho OAuth redirect.
    """
    code = request.GET.get('code')
    if not code:
        logger.warning("Zoho OAuth callback called without code.")
        return HttpResponse(
            "Missing 'code' in querystring. Use the Zoho auth URL to authorize.",
            status=400
        )

    token_url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.ZOHO_CLIENT_ID,
        "client_secret": settings.ZOHO_CLIENT_SECRET,
        "redirect_uri": "https://stablelinkcapital.com/zoho/oauth/callback/",
        "code": code,
    }

    try:
        import requests
        resp = requests.post(token_url, data=data, timeout=10)
        resp.raise_for_status()
        payload = resp.json()

        refresh_token = payload.get("refresh_token")
        if not refresh_token:
            logger.error(f"No refresh token returned by Zoho: {payload}")
            return HttpResponse(
                f"Error: No refresh token returned. Response: {payload}",
                status=500
            )

        logger.info("Zoho OAuth token exchange successful.")
        return HttpResponse(
            f"REFRESH_TOKEN: {refresh_token}\n\nPaste this into Railway as ZOHO_REFRESH_TOKEN"
        )

    except requests.RequestException as e:
        logger.error(f"Zoho token exchange failed: {e}")
        return HttpResponse(
            f"Token exchange failed: {e}",
            status=500
        )
