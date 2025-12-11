"""
Serializers for user registration and authentication.

All validation messages remain generic to avoid leaking account existence
or activation state beyond necessary guidance.
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Handle new user registration with password confirmation checks."""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password']

    def validate(self, data):
        """Ensure both password fields match before creating the user."""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        return data

    def validate_email(self, value):
        """Reject duplicate emails with a generic, security-friendly message."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Please check your input and try again.')
        return value

    def create(self, validated_data):
        """Create an inactive user; activation email is handled in the view."""
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # User must confirm email first
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Email-based login serializer with activation and credential checks."""
    username_field = 'email'

    def validate(self, attrs):
        """Validate credentials, ensure activation, and return JWT pair."""
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        # Check if user exists
        try:
            user = User.objects.get(email=email)
            
            # Check whether the account is activated
            if not user.is_active:
                raise serializers.ValidationError(
                    "Account is not activated yet. Please check your email."
                )
            
            # Check password
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid email or password.")
                
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        self.user = user
        data = super().validate(attrs)
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token
