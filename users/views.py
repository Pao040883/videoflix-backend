from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone as dj_timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .api.serializers import CustomTokenObtainPairSerializer, UserRegistrationSerializer
from .utils import (
    generate_activation_token,
    build_activation_link,
    build_password_reset_link,
    send_activation_email,
    send_password_reset_email
)
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User created: {user.email}, about to send activation email")
            self._send_activation_email_to_user(user)
            logger.info(f"Activation email function completed for {user.email}")
            
            return Response({
                'message': 'Registration successful. Please check your email to activate your account.'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_activation_email_to_user(self, user):
        """Send activation email to newly registered user"""
        logger.info(f"_send_activation_email_to_user called for {user.email}")
        uid, token = generate_activation_token(user)
        activation_link = build_activation_link(uid, token)
        logger.info(f"Activation link generated: {activation_link}")
        success = send_activation_email(user, activation_link)
        logger.info(f"send_activation_email returned: {success}")
        if not success:
            logger.error(f"Failed to send activation email to {user.email}")


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uid, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({
                    'message': 'Account successfully activated. You can now log in.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid activation link.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'error': 'Invalid activation link.'
            }, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        refresh_token = response.data.get("refresh")
        access_token = response.data.get("access")

        if refresh_token:
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=refresh_token,
                expires=dj_timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                httponly=True,
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                path="/"
            )
            del response.data["refresh"]

        response.data = {
            "access": access_token,
            "message": "Login successful."
        }
        return response



class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_cookie = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        if not refresh_cookie:
            return Response({"detail": "Refresh token cookie missing."}, status=status.HTTP_401_UNAUTHORIZED)

        from django.http import QueryDict
        qd = QueryDict(mutable=True)
        qd.update({"refresh": refresh_cookie})
        request._full_data = qd

        response = super().post(request, *args, **kwargs)

        # If rotation is enabled, a new refresh token is returned → set it again
        if "refresh" in response.data:
            new_refresh = response.data["refresh"]
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=new_refresh,
                expires=dj_timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                httponly=True,
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                path="/"
            )
            del response.data["refresh"]  # optional: nicht an Frontend senden

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response({"detail": "Token is invalid or has already expired."}, status=status.HTTP_400_BAD_REQUEST)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'], path='/')
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        })


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=400)

        try:
            user = User.objects.get(email=email)
            self._send_password_reset_email_to_user(user)
        except User.DoesNotExist:
            # Security measure: do not reveal whether the email exists
            pass

        return Response({'message': 'If a user with this email exists, an email has been sent.'})
    
    def _send_password_reset_email_to_user(self, user):
        """Send password reset email to user"""
        uid, token = generate_activation_token(user)
        reset_link = build_password_reset_link(uid, token)
        send_password_reset_email(user, reset_link)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        password1 = request.data.get('new_password1')
        password2 = request.data.get('new_password2')

        if not all([uidb64, token, password1, password2]):
            return Response({'error': 'All fields are required.'}, status=400)

        if password1 != password2:
            return Response({'error': 'Passwords do not match.'}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid user.'}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token.'}, status=400)

        user.set_password(password1)
        user.save()

        return Response({'message': 'Password has been reset successfully.'})