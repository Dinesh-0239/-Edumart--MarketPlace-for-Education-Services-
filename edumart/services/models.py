from django.db import models
from users.models import CustomUser

class Service(models.Model):
    CATEGORY_CHOICES = [
        ('Tutoring', 'Tutoring'),
        ('Graphic Design', 'Graphic Design'),
        ('App Development', 'App Development'),
        ('Web Development', 'Web Development'),
        ('Other', 'Other'),
    ]

    provider = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
