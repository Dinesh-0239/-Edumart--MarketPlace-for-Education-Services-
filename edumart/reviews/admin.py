from django.contrib import admin
from .models import Review

# Register your models here.
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('service', 'client', 'rating', 'created_at')
    search_fields = ('service__title', 'client__username')
    list_filter = ('rating',)

admin.site.register(Review, ReviewAdmin)

