from django.urls import path
from ..views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ActivateAccountView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("activate/<str:uid>/<str:token>/", ActivateAccountView.as_view(), name="activate"),
    path("login/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("reset-password/", PasswordResetRequestView.as_view(), name="reset-password"),
    path(
        "reset-password-confirm/",
        PasswordResetConfirmView.as_view(),
        name="reset-password-confirm",
    ),
]
