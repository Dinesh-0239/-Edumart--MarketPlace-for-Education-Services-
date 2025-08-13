from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from services.models import Service
from reviews.models import Review
from bookings.models import Booking  
from django.contrib import messages
from django.utils import timezone
from collections import defaultdict
from django.db.models import Count

def index(request):
    return render(request, 'index.html')

@login_required
def profile(request):
    """Handles user profile and bookings"""
    delete_past_bookings()  # Delete outdated bookings

    user = request.user

    #  Services listed by the provider (Only available services)
    services = Service.objects.filter(provider=user, available=True) if user.is_service_provider else None

    #  Client's confirmed bookings (Only for clients)
    client_bookings = Booking.objects.filter(client=user, status="Confirmed") if not user.is_service_provider else None

    #  Client's pending & approved bookings
    bookings_client = Booking.objects.filter(client=user, status__in=["Pending", "Approved"]) if not user.is_service_provider else None

    #  Provider's confirmed bookings (Only for service providers)
    provider_bookings = Booking.objects.filter(service__provider=user, status="Confirmed") if user.is_service_provider else None

    #  Completed services for clients
    client_completed_services = Booking.objects.filter(client=user, status="Completed") if not user.is_service_provider else None

    #  Completed services for providers
    provider_completed_services = Booking.objects.filter(service__provider=user, status="Completed") if user.is_service_provider else None

    #  Pending booking requests for providers
    notifications = Booking.objects.filter(service__provider=user, status="Pending") if user.is_service_provider else None

    #  Reviews given by the client
    client_reviews = Review.objects.filter(client=user) if not user.is_service_provider else None

    #  Reviews received by the service provider
    provider_reviews = Review.objects.filter(service__provider=user) if user.is_service_provider else None

        # 🔢 Get slot counts for each (service, date, time) for providers
    slot_counts = {}
    if user.is_service_provider:
        counts = Booking.objects.filter(
            service__provider=user,
            status="Confirmed",
            payment__status="Completed"  # Only count bookings with completed payments
        ).values(
            "service_id", "date", "time"
        ).annotate(total=Count("id"))

        # Convert QuerySet to dict with tuple keys (service_id, date, time)
        slot_counts = {
            (item["service_id"], str(item["date"]), str(item["time"])): item["total"]
            for item in counts
        }

    return render(request, "profile.html", {
        "user": user,
        "services": services,
        "client_bookings": client_bookings,  
        "bookings_client": bookings_client,  
        "provider_bookings": provider_bookings,
        "client_completed_services": client_completed_services,
        "provider_completed_services": provider_completed_services,
        "notifications": notifications,
        "client_reviews": client_reviews,
        "provider_reviews": provider_reviews,
        "slot_counts": slot_counts,
    })

@login_required
def manage_booking(request, booking_id, action):
    """Allow service providers to accept or reject bookings."""
    booking = get_object_or_404(Booking, id=booking_id, service__provider=request.user)
    
    if action == 'accept':
        booking.status = 'Confirmed'  # Status updated to "Confirmed"
        booking.save()
        count = Booking.get_booking_count_for_slot(booking.service, booking.date, booking.time)
        messages.success(request, f"Booking #{booking.id} has been confirmed! Total confirmed bookings for this slot: {count}")
    elif action == 'reject':
        booking.status = 'Cancelled'
        booking.save()
        messages.warning(request, f"Booking #{booking.id} has been rejected!")
    
    return redirect('profile')

def provider_profile(request, provider_id):
    """Display the profile of a service provider with their services and reviews."""
    provider = get_object_or_404(CustomUser, id=provider_id)

    # Redirect to own profile if the logged-in user is the provider
    if request.user.is_authenticated and request.user == provider:
        return redirect('profile')

    # Fetch only available services for better user experience
    services = Service.objects.filter(provider=provider, available=True)

    # Fetch all reviews for services provided by this provider
    provider_reviews = Review.objects.filter(service__provider=provider).select_related('client', 'service')

    return render(request, 'provider_profile.html', {
        'provider': provider, 
        'services': services, 
        'provider_reviews': provider_reviews
    })
    
def delete_past_bookings():
    """Delete past bookings that are neither Confirmed nor Completed.
       If a booking is Confirmed and past its date & time, mark it as Completed.
    """
    now = timezone.now()
    today = now.date()
    current_time = now.time()

    # Delete past bookings where status is neither Confirmed nor Completed
    Booking.objects.filter(date__lt=today).exclude(status__in=["Confirmed", "Completed"]).delete()
    Booking.objects.filter(date=today, time__lt=current_time).exclude(status__in=["Confirmed", "Completed"]).delete()

    # Mark Confirmed bookings as Completed if their time has passed
    # This will automatically decrease the confirmed booking count
    Booking.objects.filter(
        date__lt=today, status="Confirmed"
    ).update(status="Completed")

    Booking.objects.filter(
        date=today, time__lt=current_time, status="Confirmed"
    ).update(status="Completed")
