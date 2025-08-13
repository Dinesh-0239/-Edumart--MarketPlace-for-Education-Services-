from django.urls import path
from .views import (
    service_reviews, add_review, edit_review, delete_review, view_service_reviews, provider_reviews
)

urlpatterns = [
    path('service/<int:service_id>/', service_reviews, name="service_reviews"),  # View all reviews for a service
    path('service/<int:service_id>/add/', add_review, name="add_review"),  # Add a review
    path('review/<int:review_id>/edit/', edit_review, name="edit_review"),  # Edit a review
    path('review/<int:review_id>/delete/', delete_review, name="delete_review"),  # Delete a review
    path('service/<int:service_id>/reviews/', view_service_reviews, name="view_service_reviews"),  # View reviews for provider's service
    path('provider/reviews/', provider_reviews, name="provider_reviews"),  # View all reviews for provider's services
]
