from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking
from chat.models import ChatMessage

@receiver(post_save, sender=Booking)
def delete_chat_on_completion(sender, instance, **kwargs):
    """Deletes chat messages when a booking's status changes to 'Completed'."""
    if instance.status == "Completed":
        ChatMessage.objects.filter(
            sender=instance.client, receiver=instance.service.provider
        ).delete()
        ChatMessage.objects.filter(
            sender=instance.service.provider, receiver=instance.client
        ).delete()
