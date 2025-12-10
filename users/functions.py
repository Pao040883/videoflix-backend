"""
Helper functions for user authentication and account management.
These functions extract business logic from views to keep them lean (max 14 lines).
"""
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone as dj_timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.http import QueryDict
from rest_framework.response import Response

logger = logging.getLogger(__name__)
User = get_user_model()


def extract_user_from_activation_token(uid, token):
    """
    Extract and validate user from activation token.
    
    Returns:
        tuple: (user, error_response) where error_response is None if valid
    """
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
        
        if default_token_generator.check_token(user, token):
            return user, None
        
        return None, {'error': 'Invalid activation link.'}
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None, {'error': 'Invalid activation link.'}


def activate_user_account(user):
    """
    Activate a user account.
    
    Args:
        user: User instance to activate
    """
    user.is_active = True
    user.save()
    logger.info(f"User {user.email} account activated")


def set_refresh_token_cookie(response, refresh_token):
    """
    Set refresh token as HTTP-only cookie on response.
    
    Args:
        response: Response object to set cookie on
        refresh_token: Refresh token value
        
    Returns:
        Response: Modified response with cookie set
    """
    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=refresh_token,
        expires=dj_timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        httponly=True,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        path="/"
    )
    return response


def extract_refresh_cookie_from_request(request):
    """
    Extract refresh token cookie from request.
    
    Args:
        request: Request object
        
    Returns:
        str: Refresh token or None if not found
    """
    return request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])


def prepare_refresh_request_with_cookie(request, refresh_cookie):
    """
    Prepare QueryDict with refresh token for token refresh.
    
    Args:
        request: Request object
        refresh_cookie: Refresh token value
        
    Returns:
        Request: Modified request object
    """
    qd = QueryDict(mutable=True)
    qd.update({"refresh": refresh_cookie})
    request._full_data = qd
    return request


def validate_reset_password_fields(uidb64, token, password1, password2):
    """
    Validate password reset form fields.
    
    Returns:
        tuple: (is_valid, error_response) where error_response is None if valid
    """
    if not all([uidb64, token, password1, password2]):
        return False, {'error': 'All fields are required.'}
    
    if password1 != password2:
        return False, {'error': 'Passwords do not match.'}
    
    return True, None


def get_user_from_reset_token(uidb64, token):
    """
    Get user from password reset token.
    
    Returns:
        tuple: (user, error_response) where error_response is None if valid
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if not default_token_generator.check_token(user, token):
            return None, {'error': 'Invalid or expired token.'}
        
        return user, None
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None, {'error': 'Invalid user.'}


def update_user_password(user, new_password):
    """
    Update user password.
    
    Args:
        user: User instance
        new_password: New password value
    """
    user.set_password(new_password)
    user.save()
    logger.info(f"Password updated for user {user.email}")
