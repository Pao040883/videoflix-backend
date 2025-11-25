from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwörter stimmen nicht überein.'
            })
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Bitte überprüfe deine Eingaben und versuche es erneut.')
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # User muss Email erst bestätigen
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("E-Mail und Passwort erforderlich.")

        # Prüfe ob User existiert
        try:
            user = User.objects.get(email=email)
            
            # Prüfe ob Account aktiviert ist
            if not user.is_active:
                raise serializers.ValidationError(
                    "Account ist noch nicht aktiviert. Bitte überprüfe deine E-Mails."
                )
            
            # Prüfe Passwort
            if not user.check_password(password):
                raise serializers.ValidationError("Ungültige E-Mail oder Passwort.")
                
        except User.DoesNotExist:
            raise serializers.ValidationError("Ungültige E-Mail oder Passwort.")

        self.user = user
        data = super().validate(attrs)
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token
