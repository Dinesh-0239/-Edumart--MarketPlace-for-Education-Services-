import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.crypto import get_random_string

from users.models import CustomUser
from services.models import Service
from bookings.models import Booking
from payments.models import Payment
from reviews.models import Review

# Function to generate a secure OTP
def generate_otp():
    return get_random_string(6, allowed_chars='0123456789')

# Function to send OTP via email
def send_otp_email(email, otp, subject):
    message = f"Your OTP is: {otp}. Do not share this with anyone."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

# -------------------------
# User Registration Views
# -------------------------
def register(request):
    """ Handles user registration with OTP verification """
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        is_service_provider = request.POST.get("is_service_provider") == "on"
        bio = request.POST.get("bio", "")
        profile_picture = request.FILES.get("profile_picture")

        # Password match check
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        # Gmail domain check
        if not email.endswith('@gmail.com'):
            messages.error(request,"Only @gmail.com email addresses are allowed.")
            return redirect("register")
        
        # Check if user with this email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect("register")

        # Save the uploaded file temporarily
        temp_profile_pic = None
        if profile_picture:
            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', profile_picture.name)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, 'wb+') as destination:
                for chunk in profile_picture.chunks():
                    destination.write(chunk)
            temp_profile_pic = os.path.join('temp', profile_picture.name)

        # Generate OTP and store registration info in session
        otp = generate_otp()
        request.session["pending_registration"] = {
            "username": username,
            "email": email,
            "password": make_password(password1),  # Use password1 after validation
            "is_service_provider": is_service_provider,
            "bio": bio,
            "temp_profile_pic": temp_profile_pic,
        }
        request.session["registration_otp"] = otp
        request.session.set_expiry(600)  # OTP expires in 10 minutes

        send_otp_email(email, otp, "EduMart OTP Verification")
        messages.success(request, "OTP sent to your email. Please verify.")
        return redirect("verify_otp")

    return render(request, "users/register.html")

def verify_otp(request):
    """ Verifies the OTP entered by the user """
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        session_otp = request.session.get("registration_otp")
        user_data = request.session.get("pending_registration")

        if user_data and entered_otp == session_otp:
            # Remove profile picture from user_data before creating user
            temp_profile_pic = user_data.pop("temp_profile_pic", None)
            
            user = CustomUser.objects.create(**user_data)
            
            # Handle profile picture if it exists
            if temp_profile_pic:
                temp_path = os.path.join(settings.MEDIA_ROOT, temp_profile_pic)
                if os.path.exists(temp_path):
                    with open(temp_path, 'rb') as f:
                        user.profile_picture.save(
                            os.path.basename(temp_profile_pic),
                            f,
                            save=True
                        )
                    # Clean up temporary file
                    os.remove(temp_path)
            
            del request.session["registration_otp"]
            del request.session["pending_registration"]
            messages.success(request, "Registration successful! You can now log in.")
            return redirect("login")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    
    return render(request, "users/verify_otp.html")

def resend_otp(request):
    """ Resends a new OTP if session is valid """
    user_email = request.session.get("pending_registration", {}).get("email")
    if user_email:
        new_otp = generate_otp()
        request.session["registration_otp"] = new_otp
        send_otp_email(user_email, new_otp, "EduMart OTP Resend")
        messages.success(request, "A new OTP has been sent to your email.")
        return redirect("verify_otp")
    messages.error(request, "Session expired. Please register again.")
    return redirect("register")

# -------------------------
# User Authentication Views
# -------------------------

def user_login(request):
    """ Handles user login manually """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("profile")
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    return render(request, "users/login.html")


@login_required
def edit_profile(request):
    """Allows users to edit their profile (except email)."""
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username")
        bio = request.POST.get("bio")
        profile_picture = request.FILES.get("profile_picture")

        # Update username and bio
        user.username = username
        user.bio = bio

        # Update profile picture if a new one is uploaded
        if profile_picture:
            user.profile_picture = profile_picture

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "users/edit_profile.html", {"user": user})

def user_logout(request):
    """ Logs out the user """
    logout(request)
    return redirect("index")

# -------------------------
# Password Reset Views
# -------------------------

def request_password_reset(request):
    """ Handles password reset requests """
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        try:
            user = CustomUser.objects.get(username=username, email=email)
            otp = generate_otp()
            request.session["password_reset_otp"] = otp
            request.session["reset_user"] = user.email
            request.session.set_expiry(600)
            send_otp_email(email, otp, "EduMart Password Reset OTP")
            messages.success(request, "OTP sent to your email.")
            return redirect("verify_password_otp")
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid username or email.")
    return render(request, "users/request_password_reset.html")

def verify_password_otp(request):
    """ Verifies the OTP for password reset """
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        if entered_otp == request.session.get("password_reset_otp"):
            return redirect("reset_password")
        messages.error(request, "Invalid OTP.")
    return render(request, "users/verify_password_otp.html")

def reset_password(request):
    """ Resets the user's password """
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        if new_password == confirm_password:
            user = CustomUser.objects.get(email=request.session.get("reset_user"))
            user.password = make_password(new_password)
            user.save()
            del request.session["password_reset_otp"]
            del request.session["reset_user"]
            messages.success(request, "Password reset successfully.")
            return redirect("login")
        messages.error(request, "Passwords do not match.")
    return render(request, "users/reset_password.html")