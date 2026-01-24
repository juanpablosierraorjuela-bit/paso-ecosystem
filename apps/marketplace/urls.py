from django.urls import path
from . import views

urlpatterns = [
    # Navegación Principal
    path('', views.home, name='marketplace_home'),
    path('salon/<int:pk>/', views.salon_detail, name='salon_detail'),

    # Flujo de Reserva (Wizard)
    # Ejemplo de uso: /marketplace/book/5/?services=1,2
    path('book/<int:salon_id>/', views.booking_wizard, name='booking_wizard'),
    path('book/commit/', views.booking_commit, name='booking_commit'),
    
    # API para carga dinámica de horas (AJAX)
    path('api/slots/', views.get_available_slots_api, name='api_get_slots'),

    # Espacio del Cliente
    path('mi-perfil/', views.client_dashboard, name='client_dashboard'),
    path('cita/<int:pk>/cancelar/', views.cancel_appointment, name='cancel_appointment'),
]