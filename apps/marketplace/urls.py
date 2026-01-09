from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='marketplace_home'), # Home del Market
    path('salon/<int:pk>/', views.salon_detail, name='salon_detail'),
    path('reservar/<int:salon_id>/<int:service_id>/', views.booking_wizard, name='booking_wizard'),
]