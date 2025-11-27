from django.shortcuts import render

def home_view(request):
    return render(request, 'home/index.html')


from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings

def test_email(request):
    try:
        print("📧 Sending test email...")  # will appear in Railway logs

        send_mail(
            subject="Test Email from StableLinkCapital",
            message="This confirms your email settings are working!",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["vanessavaldezwhite@gmail.com"],
            fail_silently=False,
        )

        print("✅ Email successfully sent!")  # appears in Railway logs

        return HttpResponse("Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")  # will appear in logs
        return HttpResponse(f"Error: {e}")
