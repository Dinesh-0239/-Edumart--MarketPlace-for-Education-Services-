from django.shortcuts import redirect
from django.urls import reverse

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_required_paths = [
            "/profile", "/provider_profile/", "/services/", "/bookings/", "/payments/", "/reviews/", "/chat/"
        ]
        self.guest_only_paths = [
            "/", "/users/register/", "/users/login/", "/users/verify-otp/", "/users/resend-otp/",
            "/users/password-reset/", "/users/verify-password-otp/", "/users/reset-password/"
        ]
        self.admin_panel_path = "/admin/"
        self.logout_path = "/users/logout/"

    def __call__(self, request):
        path = request.path_info

        # 🛑 Allow admin to logout properly
        if path == "/admin/logout/":
            return self.get_response(request)  # ✅ Allow normal processing

        if request.user.is_authenticated and request.user.is_superuser:
            if not path.startswith(self.admin_panel_path):
                return redirect(self.admin_panel_path)

        if path in self.guest_only_paths and request.user.is_authenticated:
            return redirect("/profile")

        if path in self.auth_required_paths and not request.user.is_authenticated:
            return redirect("/users/login/")

        if path.startswith("/bookings/create/"):
            if request.user.is_authenticated and hasattr(request.user, "is_service_provider") and request.user.is_service_provider:
                return redirect(reverse("profile"))

        response = self.get_response(request)
        return response
