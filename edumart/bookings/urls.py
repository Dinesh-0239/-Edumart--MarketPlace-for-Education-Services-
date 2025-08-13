from django.urls import path
from .views import (
    booking_list, 
    create_booking, 
    cancel_booking, 
    accept_booking, 
    reject_booking,
    get_slot_booking_count  
)

urlpatterns = [
    path('', booking_list, name="booking_list"),
    path('create/<int:service_id>/', create_booking, name="create_booking"),
    path('<int:booking_id>/cancel/', cancel_booking, name="cancel_booking"),
    path('<int:booking_id>/accept/', accept_booking, name="accept_booking"),
    path('<int:booking_id>/reject/', reject_booking, name="reject_booking"),

    #  New AJAX route for slot booking count
    path('slot-booking-count/', get_slot_booking_count, name="get_slot_booking_count"),
]
