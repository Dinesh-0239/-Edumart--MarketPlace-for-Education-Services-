from django.urls import path
from .views import make_payment, initiate_payment, payment_success

urlpatterns = [
    path('pay/<int:booking_id>/', make_payment, name="make_payment"),  # Redirects to initiate_payment
    path('initiate/<int:booking_id>/', initiate_payment, name="initiate_payment"),  # Starts Razorpay order
    path('success/', payment_success, name="payment_success"),  # Handles success response
]
