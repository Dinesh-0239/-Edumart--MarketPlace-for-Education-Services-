from django.urls import path
from .views import service_list, create_service, update_service, delete_service, search_services

urlpatterns = [
    path('search/', search_services, name='search_services'),
    path('', service_list, name="service_list"),
    path('create/', create_service, name="create_service"),
    path('<int:service_id>/update/', update_service, name="update_service"),
    path('<int:service_id>/delete/', delete_service, name="delete_service"),
]
