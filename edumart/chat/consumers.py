import json
from channels.generic.websocket import AsyncWebsocketConsumer
from users.models import CustomUser as User
from .models import ChatMessage
from bookings.models import Booking  # ✅ Import Booking model
from django.core.exceptions import ObjectDoesNotExist


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['booking_id']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Receive and process incoming messages."""
        data = json.loads(text_data)
        message = data.get('message', "").strip()
        receiver_id = data.get('receiver_id')
        sender = self.scope["user"]

        if not message:
            return  # Ignore empty messages

        # ✅ Fetch the booking instance
        try:
            booking = await Booking.objects.aget(id=int(self.room_name))  # Ensure booking exists
        except ObjectDoesNotExist:
            return  # Ignore if booking does not exist

        # ✅ Handle invalid receiver_id properly
        try:
            receiver = await User.objects.aget(id=receiver_id)
        except ObjectDoesNotExist:
            return  # Ignore if receiver does not exist

        # ✅ Save message with `booking_id`
        chat_message = await ChatMessage.objects.acreate(
            sender=sender,
            receiver=receiver,
            message=message,
            booking=booking  # ✅ Assign booking
        )

        # ✅ Refresh object to get correct timestamp
        await self.send_chat_message(chat_message, sender.username, receiver.username)

    async def send_chat_message(self, chat_message, sender_username, receiver_username):
        """Send message data to WebSocket group."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': chat_message.message,
                'sender': sender_username,
                'receiver': receiver_username,
                'timestamp': chat_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        )

    async def chat_message(self, event):
        """Send message data to WebSocket."""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'receiver': event['receiver'],
            'timestamp': event['timestamp']
        }))
