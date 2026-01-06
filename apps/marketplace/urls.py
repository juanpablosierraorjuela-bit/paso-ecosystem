from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_home, name='home'),
    path('salon/<int:pk>/', views.salon_detail, name='salon_detail'),
    path('reservar/<int:service_id>/', views.booking_create, name='booking_create'),
    path('reserva-exitosa/<int:pk>/', views.booking_success, name='booking_success'),
]