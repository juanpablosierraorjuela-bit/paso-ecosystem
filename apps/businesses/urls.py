from django.urls import path
from . import views

urlpatterns = [
    # --- BOTÓN DE PÁNICO (Solo Admin) ---

    # Rutas Publicas
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('registro-negocio/', views.register_owner, name='register_owner'),
    
    # Dashboards
    path('panel/dueno/', views.owner_dashboard, name='admin_dashboard'),
    path('panel/cliente/', views.dashboard, name='dashboard'),
    path('panel/empleado/', views.employee_dashboard, name='employee_panel'),
    
    # Acciones
    path('servicios/eliminar/<int:service_id>/', views.delete_service, name='delete_service'),
    path('logout/', views.logout_view, name='logout'),
    
    # Reservas
    path('reservar/<slug:salon_slug>/', views.booking_create, name='booking_create'),
    path('reserva/exito/<int:booking_id>/', views.booking_success, name='booking_success'),
    
    # API y Webhooks
    path('api/slots/', views.get_available_slots_api, name='api_slots'),
    path('api/webhooks/bold/<int:salon_id>/', views.bold_webhook, name='bold_webhook'),
    path('api/test-telegram/', views.test_telegram_integration, name='test_telegram'),
]
