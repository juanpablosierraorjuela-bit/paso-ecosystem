from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='marketplace_home'),
    path('salon/<int:pk>/', views.salon_detail, name='salon_detail'),
    # Cambio: El wizard ya no pide service_id en el path, los recibe por parámetro GET
    path('book/<int:salon_id>/', views.booking_wizard, name='booking_wizard'),
    path('api/slots/', views.get_available_slots_api, name='api_get_slots'),
    path('book/commit/', views.booking_commit, name='booking_commit'),
    path('appointment/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
]