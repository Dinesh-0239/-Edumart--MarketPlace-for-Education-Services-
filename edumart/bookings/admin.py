from django.contrib import admin
from .models import Booking

# Register your models here.
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'date', 'time', 'status', 'created_at')
    search_fields = ('client__username', 'service__title')
    list_filter = ('status', 'date')

admin.site.register(Booking, BookingAdmin)

