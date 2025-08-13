from django.contrib import admin
from .models import Payment

# Register your models here.
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'payment_id', 'amount', 'status', 'created_at')
    search_fields = ('payment_id', 'booking__client__username')
    list_filter = ('status',)

admin.site.register(Payment, PaymentAdmin)

