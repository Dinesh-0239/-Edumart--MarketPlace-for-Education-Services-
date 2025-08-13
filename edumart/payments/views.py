import razorpay
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from bookings.models import Booking
from .models import Payment

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Razorpay Client with test mode
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

def make_payment(request, booking_id):
    """Redirect to payment initiation page"""
    booking = get_object_or_404(Booking, id=booking_id, client=request.user)
    
    # Check if payment already exists
    if Payment.objects.filter(booking=booking, status="Completed").exists():
        messages.info(request, "This booking has already been paid for.")
        return redirect("profile")
        
    return redirect("initiate_payment", booking_id=booking.id)

def initiate_payment(request, booking_id):
    """Initialize payment and show payment page"""
    booking = get_object_or_404(Booking, id=booking_id, client=request.user)

    # Check for existing payment
    try:
        payment = Payment.objects.get(booking=booking)
        if payment.status == "Completed":
            messages.info(request, "This booking has already been paid for.")
            return redirect("profile")
        # If payment exists but not completed, update it
        amount = int(booking.service.price * 100)  # Convert to paise
    except Payment.DoesNotExist:
        # Create new payment if none exists
        amount = int(booking.service.price * 100)  # Convert to paise

    try:
        # Create Razorpay Order
        order_data = {
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        }
        
        order = razorpay_client.order.create(order_data)
        logger.info(f"Created Razorpay order: {order['id']}")

        # Update or create payment record
        payment, created = Payment.objects.update_or_create(
            booking=booking,
            defaults={
                'payment_id': order['id'],
                'amount': booking.service.price,
                'status': "Pending"
            }
        )

        # Test card information
        test_cards = {
            "success": {
                "number": "4111 1111 1111 1111",
                "cvv": "123",
                "expiry": "12/25"
            },
            "failure": {
                "number": "4242 4242 4242 4242",
                "cvv": "123",
                "expiry": "12/25"
            }
        }

        context = {
            "booking": booking,
            "order_id": order['id'],
            "razorpay_merchant_key": settings.RAZORPAY_API_KEY,
            "amount": amount,
            "currency": "INR",
            "test_cards": test_cards,
            "callback_url": request.build_absolute_uri(reverse('payment_success'))
        }
        
        logger.info(f"Rendering payment page for booking {booking_id}")
        return render(request, "payments/payment_page.html", context)

    except Exception as e:
        logger.error(f"Payment initiation failed: {str(e)}")
        messages.error(request, "Failed to initiate payment. Please try again.")
        return redirect("profile")

def payment_success(request):
    """Handle successful payment callback"""
    if request.method == "POST":
        try:
            params_dict = {
                'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
                'razorpay_order_id': request.POST.get('razorpay_order_id'),
                'razorpay_signature': request.POST.get('razorpay_signature')
            }
            
            logger.info(f"Received payment callback: {params_dict}")

            try:
                # Verify payment signature
                razorpay_client.utility.verify_payment_signature(params_dict)
                
                # Update payment status
                payment = Payment.objects.get(payment_id=params_dict['razorpay_order_id'])
                payment.status = "Completed"
                payment.save()

                # Update booking status
                booking = payment.booking
                booking.status = "Confirmed"
                booking.save()

                messages.success(request, "Payment successful! Your booking is confirmed.")
                return redirect('profile')

            except Exception as e:
                logger.error(f"Payment verification failed: {str(e)}")
                messages.error(request, "Payment verification failed. Please contact support.")
                return redirect('profile')

        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            messages.error(request, "Payment processing failed. Please try again.")
            return redirect('profile')

    return redirect('profile')
