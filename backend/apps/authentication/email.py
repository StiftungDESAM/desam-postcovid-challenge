from django.core.mail import EmailMessage, get_connection


from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

def test_email(request,email_recipient):
    
    logger.debug("Die Test Email Funktion wurde aufgerufen")
    
    #insert link/code gerneration
    link = "www.this is alink.de/registration/123"
    #email recipient is in our case the email, if thats not the case fetch email here
    email = email_recipient
    code_msg = "Dear User, your code is " + link + "please click this link"
    try:
        logger.debug("Trying to send email to {email}.")
        send_mail(
            "PostCovidDatabase: Your Registration Code",
            link,
            "postcovid@reutlingen-university.de",
            [email],
            fail_silently=False,

            )
        logger.info("Email successfully send to {email}")
    except Exception as e:
        logger.debug(f"Failed to send email to {email} with exception + {str(e)}")
        raise ConnectionRefusedError
    #(f"Failed to send email to {email} with exception + {str(e)}")
        
    request.session['email_sent'] = True

    return 0
 