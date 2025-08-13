from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    register, verify_otp, resend_otp, user_login, user_logout,
    request_password_reset, verify_password_otp, reset_password,edit_profile
)

urlpatterns = [
    path("register/", register, name="register"),
    path("edit-profile/", edit_profile, name="edit_profile"),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("resend-otp/", resend_otp, name="resend_otp"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("password-reset/", request_password_reset, name="request_password_reset"),
    path("verify-password-otp/", verify_password_otp, name="verify_password_otp"),
    path("reset-password/", reset_password, name="reset_password"),
]

# Ensure media file serving only in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
