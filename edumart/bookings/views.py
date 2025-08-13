from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from services.models import Service
from .models import Booking

# List All Bookings for Clients
@login_required
def booking_list(request):
    bookings = Booking.objects.filter(client=request.user).order_by('-created_at')
    return render(request, "bookings/booking_list.html", {"bookings": bookings})

# Create a New Booking
@login_required
def create_booking(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        date = request.POST.get("date")
        time = request.POST.get("time")

        if not date or not time:
            messages.error(request, "Please provide both date and time.")
            return render(request, "bookings/booking_form.html", {"service": service})

        try:
            selected_date = timezone.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return render(request, "bookings/booking_form.html", {"service": service})

        today = timezone.localdate()
        next_day = today + timedelta(days=1)

        if selected_date < next_day:
            messages.error(request, "Bookings must be made at least one day in advance.")
            return render(request, "bookings/booking_form.html", {"service": service})

        active_booking_exists = Booking.objects.filter(
            client=request.user,
            service=service,
            service__provider=service.provider
        ).exclude(status__in=["Completed", "Cancelled"]).exists()

        if active_booking_exists:
            messages.error(request, "You already have an active booking for this service.")
            return render(request, "bookings/booking_form.html", {"service": service})

        # Booking count for feedback (no limit)
        existing_count = Booking.get_booking_count_for_slot(service, selected_date, time)

        booking = Booking(
            client=request.user,
            service=service,
            date=selected_date,
            time=time,
            status="Pending"
        )
        booking.save()
        messages.success(request, f"Booking request sent! {existing_count + 1} client(s) have booked this slot.")
        return redirect("profile")

    return render(request, "bookings/booking_form.html", {"service": service})

# Cancel Booking
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, client=request.user)

    if request.method == "POST":
        if booking.status in ["Pending", "Approved", "Confirmed"]:
            booking.status = "Cancelled"
            booking.save()
            messages.success(request, "Booking cancelled successfully.")
        else:
            messages.error(request, "This booking cannot be cancelled.")
        return redirect("profile")

    return render(request, "bookings/booking_cancel.html", {"booking": booking})

# Accept Booking (for Service Providers)
@login_required
def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, service__provider=request.user)

    if booking.status == "Pending":
        booking.status = "Approved"
        booking.save()
        count = Booking.get_booking_count_for_slot(booking.service, booking.date, booking.time)
        messages.success(request, f"Booking approved! Total bookings for this slot: {count}")
    else:
        messages.error(request, "This booking cannot be approved.")

    return redirect("profile")

# Reject Booking
@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, service__provider=request.user)

    if request.method == "POST":
        if booking.status == "Pending":
            booking.status = "Cancelled"
            booking.save()
            messages.success(request, "Booking rejected successfully.")
        else:
            messages.error(request, "This booking cannot be rejected.")
        return redirect("profile")

    return render(request, "bookings/booking_reject.html", {"booking": booking, "action": "Reject"})

#  API to return count of bookings for a given slot (AJAX support)
@login_required
def get_slot_booking_count(request):
    service_id = request.GET.get("service_id")
    date = request.GET.get("date")
    time = request.GET.get("time")

    if not (service_id and date and time):
        return JsonResponse({"count": 0})

    count = Booking.objects.filter(
        service_id=service_id,
        date=date,
        time=time,
        status="Confirmed",
        payment__status="Completed"  # Only count bookings with completed payments
    ).count()

    return JsonResponse({"count": count})
