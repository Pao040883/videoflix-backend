"""
Utility functions for user authentication and email handling
"""
import logging
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

logger = logging.getLogger(__name__)


def generate_activation_token(user):
    """
    Generate activation token and UID for user account activation
    
    Args:
        user: User instance
        
    Returns:
        tuple: (uid, token)
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid, token


def build_activation_link(uid, token):
    """
    Build activation link for email
    
    Args:
        uid: User ID (base64 encoded)
        token: Activation token
        
    Returns:
        str: Full activation URL
    """
    return f"{settings.FRONTEND_URL}/activate/{uid}/{token}"


def build_password_reset_link(uid, token):
    """
    Build password reset link for email
    
    Args:
        uid: User ID (base64 encoded)
        token: Reset token
        
    Returns:
        str: Full password reset URL
    """
    return f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"


def send_activation_email(user, activation_link):
    """
    Send account activation email to user
    
    Args:
        user: User instance
        activation_link: Full activation URL
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        html_content = render_to_string('emails/activation.html', {
            'user': user,
            'activation_link': activation_link
        })
        
        email = EmailMultiAlternatives(
            subject='Aktiviere deinen Videoflix Account',
            body='Bitte aktiviere deinen Account über den Link in dieser Email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Activation email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending activation email to {user.email}: {e}")
        return False


def send_password_reset_email(user, reset_link):
    """
    Send password reset email to user
    
    Args:
        user: User instance
        reset_link: Full password reset URL
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        html_content = render_to_string("emails/password_reset.html", {
            "user": user,
            "reset_link": reset_link
        })
        
        text_content = f"Klicke auf den folgenden Link, um dein Passwort zurückzusetzen:\n{reset_link}"
        
        email = EmailMultiAlternatives(
            subject="Passwort zurücksetzen",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending password reset email to {user.email}: {e}")
        return False
