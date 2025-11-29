

# import logging
# from django.shortcuts import render, redirect
# from .models import WalletAsset, ConnectWallet
# from .forms import ConnectWalletForm
# from django.contrib.auth.decorators import login_required
# from django.core.mail import send_mail, BadHeaderError
# from django.conf import settings
# from django.urls import reverse
# import smtplib

# # Configure logging
# logger = logging.getLogger(__name__)

# @login_required
# def select_wallet(request):
#     wallets = WalletAsset.objects.all()
#     connected_wallets = ConnectWallet.objects.filter(user=request.user)

#     logger.debug(f"User {request.user.username} has {connected_wallets.count()} connected wallets.")

#     if request.method == 'POST':
#         logger.debug(f"POST data received: {request.POST}")
#         form = ConnectWalletForm(request.POST)
        
#         if form.is_valid():
#             logger.debug("Form is valid. Attempting to save ConnectWallet instance.")
#             try:
#                 connect_wallet = form.save(commit=False)
#                 connect_wallet.user = request.user
#                 connect_wallet.save()
#                 logger.info(f"ConnectWallet instance saved for user {request.user.username}.")

#                 # Try sending email, but don't break the flow if it fails
#                 try:
#                     send_mail(
#                         subject="Wallet Connected Successfully",
#                         message=f"Hello {request.user.username},\n\nYour wallet ({connect_wallet.wallet.name}) has been successfully connected.\n\nThank you!",
#                         from_email=settings.EMAIL_HOST_USER,
#                         recipient_list=[request.user.email],
#                         fail_silently=True,  # <-- prevents raising error
#                     )

#                     admin_email = 'admin@example.com'
#                     send_mail(
#                         subject=f"New Wallet Connected by {request.user.username}",
#                         message=f"Hello Admin,\n\nUser {request.user.username} has connected a new wallet: {connect_wallet.wallet.name}.",
#                         from_email=settings.EMAIL_HOST_USER,
#                         recipient_list=[admin_email],
#                         fail_silently=True,  # <-- prevents raising error
#                     )
#                     logger.info("Attempted to send emails (fail_silently=True).")

#                 except Exception as e:
#                     logger.warning(f"Email sending failed but ignored: {e}")

#                 # Always go to success page even if email fails
#                 return redirect('wallet_connection_success')

#             except Exception as e:
#                 logger.error(f"Unexpected error occurred while saving wallet: {e}")
#                 error_message = f"Unexpected error occurred while saving wallet: {e}"
#                 return redirect(reverse('error_page') + f'?error_message={error_message}')

#         else:
#             logger.warning("Form is invalid. Errors:")
#             for field, errors in form.errors.items():
#                 logger.warning(f"{field}: {', '.join(errors)}")
#             error_message = "Form submission is invalid. Please correct the errors."
#             return redirect(reverse('error_page') + f'?error_message={error_message}')

#     else:
#         logger.debug("GET request received.")
#         form = ConnectWalletForm()

#     return render(request, 'connectwallet/connect_wallet.html', {
#         'form': form,
#         'wallets': wallets,
#         'connected_wallets': connected_wallets,
#     })


# @login_required
# def wallet_connection_success(request):
#     return render(request, 'connectwallet/wallet_connection_success.html')


# @login_required
# def error_page(request):
#     error_message = request.GET.get('error_message', 'An unknown error occurred. Please try again later.')
#     return render(request, 'connectwallet/error_page.html', {
#         'error_message': error_message
#     })



import logging
from django.shortcuts import render, redirect
from .models import WalletAsset, ConnectWallet
from .forms import ConnectWalletForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from utils.email_utils import send_resend_email  # <-- Resend API

# Configure logging
logger = logging.getLogger(__name__)

@login_required
def select_wallet(request):
    wallets = WalletAsset.objects.all()
    connected_wallets = ConnectWallet.objects.filter(user=request.user)

    logger.debug(f"User {request.user.username} has {connected_wallets.count()} connected wallets.")

    if request.method == 'POST':
        logger.debug(f"POST data received: {request.POST}")
        form = ConnectWalletForm(request.POST)
        
        if form.is_valid():
            logger.debug("Form is valid. Attempting to save ConnectWallet instance.")
            try:
                connect_wallet = form.save(commit=False)
                connect_wallet.user = request.user
                connect_wallet.save()
                logger.info(f"ConnectWallet instance saved for user {request.user.username}.")

                # Try sending email, but don't break the flow if it fails
                try:
                    # --- USER EMAIL ---
                    user_email_html = (
                        f"<h3>Wallet Connected Successfully</h3>"
                        f"<p>Hello {request.user.username},</p>"
                        f"<p>Your wallet <strong>{connect_wallet.wallet.name}</strong> has been successfully connected.</p>"
                        f"<p>Thank you!</p>"
                    )
                    send_resend_email(
                        to=request.user.email,
                        subject="Wallet Connected Successfully",
                        html=user_email_html
                    )

                    # --- ADMIN EMAIL ---
                    admin_email_html = (
                        f"<h3>New Wallet Connected</h3>"
                        f"<p>User {request.user.username} has connected a new wallet: <strong>{connect_wallet.wallet.name}</strong>.</p>"
                    )
                    send_resend_email(
                        to=settings.ADMIN_EMAIL,
                        subject=f"New Wallet Connected by {request.user.username}",
                        html=admin_email_html
                    )

                    logger.info("Emails sent successfully via Resend API.")

                except Exception as e:
                    logger.warning(f"Email sending failed but ignored: {e}")

                # Always go to success page even if email fails
                return redirect('wallet_connection_success')

            except Exception as e:
                logger.error(f"Unexpected error occurred while saving wallet: {e}")
                error_message = f"Unexpected error occurred while saving wallet: {e}"
                return redirect(reverse('error_page') + f'?error_message={error_message}')

        else:
            logger.warning("Form is invalid. Errors:")
            for field, errors in form.errors.items():
                logger.warning(f"{field}: {', '.join(errors)}")
            error_message = "Form submission is invalid. Please correct the errors."
            return redirect(reverse('error_page') + f'?error_message={error_message}')

    else:
        logger.debug("GET request received.")
        form = ConnectWalletForm()

    return render(request, 'connectwallet/connect_wallet.html', {
        'form': form,
        'wallets': wallets,
        'connected_wallets': connected_wallets,
    })


@login_required
def wallet_connection_success(request):
    return render(request, 'connectwallet/wallet_connection_success.html')


@login_required
def error_page(request):
    error_message = request.GET.get('error_message', 'An unknown error occurred. Please try again later.')
    return render(request, 'connectwallet/error_page.html', {
        'error_message': error_message
    })
