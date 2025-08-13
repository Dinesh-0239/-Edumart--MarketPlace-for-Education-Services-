from django.db import models
from users.models import CustomUser
from services.models import Service

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]

    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.username} - {self.service.title} ({self.date} {self.time})"

    def get_booking_count(self):
        """
        Returns total number of bookings with completed payments for the same service, date, and time.
        Includes the current booking if it has a completed payment.
        """
        return Booking.objects.filter(
            service=self.service,
            date=self.date,
            time=self.time,
            status="Confirmed",
            payment__status="Completed"
        ).count()

    @classmethod
    def get_booking_count_for_slot(cls, service, date, time):
        """
        Class method to get booking count with completed payments for a given service, date, and time.
        Useful in forms or views before creating a booking.
        """
        return cls.objects.filter(
            service=service,
            date=date,
            time=time,
            status="Confirmed",
            payment__status="Completed"
        ).count()

    @classmethod
    def get_slot_summary(cls):
        """
        Returns a list of slots with total bookings that have completed payments.
        Useful for provider dashboards.
        """
        return cls.objects.filter(
            status="Confirmed",
            payment__status="Completed"
        ).values('service__title', 'date', 'time').annotate(
            total=models.Count('id')
        ).order_by('-total')
