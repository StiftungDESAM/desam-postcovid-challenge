from django.core.mail import EmailMessage, get_connection
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils.html import strip_tags

import logging
from config import settings

logger = logging.getLogger(__name__)

def test_email(request, email_recipient):
    
    logger.debug("Die Test Email Funktion wurde aufgerufen")
    
    #insert link/code gerneration
    link = "www.this is alink.de/registration/123"
    #email recipient is in our case the email, if thats not the case fetch email here
    email = email_recipient
    logger.debug(f"Trying to send email to {email}.")
    send_mail(
        "PostCovidDatabase: Your Registration Code",
        link,
        settings.EMAIL_SENDER,
        [email],
        fail_silently=False,

        )
    logger.info(f"Email successfully send to {email}")
        
    request.session['email_sent'] = True

    return 0

def create_verification_link(code):
    link = f"{settings.BASE_URL}/api/user/email-verification?code={code}"
    logger.debug(f"Creating verification link {link}")
    return link

def create_reset_link(code):
    link = f"{settings.BASE_URL}/page/password-reset?code={code}"
    logger.debug(f"Creating password reset link {link}")
    return link

def send_email(recipient_list, subject, message, sender=settings.EMAIL_SENDER):
    logger.debug(f"Sending email from {sender} to {', '.join(recipient_list)} with subject {subject}")

    plain_message = strip_tags(message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=message,
            from_email=sender,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f"Email successfully sent from {sender} to {', '.join(recipient_list)}")
    except Exception as e:
        logger.info(f"Couldn't send email from {sender} to {', '.join(recipient_list)} with subject {subject} and message {message}")
        logger.error(e)
        
    return