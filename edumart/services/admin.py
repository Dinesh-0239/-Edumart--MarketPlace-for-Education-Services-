from django.contrib import admin
from .models import Service

# Register your models here.
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'category', 'price', 'available', 'created_at')
    search_fields = ('title', 'provider__username', 'category')
    list_filter = ('category', 'available')

admin.site.register(Service, ServiceAdmin)

