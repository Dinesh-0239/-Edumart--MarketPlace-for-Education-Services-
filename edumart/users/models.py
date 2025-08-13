from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Custom User model extending AbstractUser with additional fields."""
    is_service_provider = models.BooleanField(default=False)  
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='profile_pics/default.png')
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.email})"
