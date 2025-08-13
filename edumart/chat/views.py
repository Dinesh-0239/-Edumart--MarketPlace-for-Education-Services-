from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from users.models import CustomUser as User
from .models import ChatMessage
from bookings.models import Booking

@login_required
def chat_room(request, booking_id):
    """Ensure only confirmed booking participants (client & provider) can chat."""
    booking = get_object_or_404(
        Booking.objects.select_related("service__provider", "client"),
        id=booking_id,
        status="Confirmed"
    )
    provider = booking.service.provider
    client = booking.client

    # Check if the current user is either the client or the provider
    if request.user not in [client, provider]:
        return HttpResponseForbidden("Unauthorized access")
    
    # Determine the receiver (the other participant in the chat)
    receiver = client if request.user == provider else provider

    # Fetch messages for the chat (filtered by booking)
    messages = ChatMessage.objects.filter(
        booking=booking  # Ensure messages belong to this booking
    ).order_by("timestamp")

    return render(request, "chat/chat_room.html", {
        "booking": booking,
        "provider": provider,
        "client": client,
        "messages": messages,
        "receiver": receiver,
    })

@login_required
def fetch_messages(request, booking_id):
    """Return chat messages for the given booking."""
    booking = get_object_or_404(Booking, id=booking_id, status="Confirmed")
    provider = booking.service.provider
    client = booking.client

    if request.user not in [client, provider]:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    messages = ChatMessage.objects.filter(
        booking=booking  # Ensure messages belong to this booking
    ).order_by("timestamp")

    return JsonResponse({
        "messages": [
            {
                "sender": msg.sender.username,
                "receiver": msg.receiver.username,
                "message": msg.message,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for msg in messages
        ]
    })