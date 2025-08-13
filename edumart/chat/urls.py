from django.urls import path
from .views import chat_room, fetch_messages  # ✅ fetch_messages import karo

urlpatterns = [
    path('<int:booking_id>/', chat_room, name='chat_room'),
    path('messages/<int:booking_id>/', fetch_messages, name='fetch_messages'),  # ✅ Add this route
]
