from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='marketplace_home'),
    path('salon/<int:pk>/', views.salon_detail, name='salon_detail'),
    path('reservar/<int:salon_id>/<int:service_id>/', views.booking_wizard, name='booking_wizard'),
    
    # Rutas Nuevas
    path('api/slots/', views.get_available_slots_api, name='api_get_slots'),
    path('reservar/confirmar/', views.booking_commit, name='booking_commit'),
]