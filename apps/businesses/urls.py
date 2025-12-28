from django.urls import path
from . import views

urlpatterns = [
    # Vista principal
    path('', views.home, name='home'),
    
    # Usuarios y Registro
    path('registro-dueno/', views.register_owner, name='register_owner'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/admin/', views.owner_dashboard, name='admin_dashboard'),
    path('dashboard/cliente/', views.dashboard, name='dashboard'),
    path('dashboard/empleado/', views.employee_dashboard, name='employee_panel'),
    path('dashboard/empleado/eliminar-horario/', views.employee_dashboard, name='employee_delete_schedule'), # Soporte para POST
    
    # Servicios y Configuración
    path('servicio/eliminar/<int:service_id>/', views.delete_service, name='delete_service'),
    path('api/slots/', views.get_available_slots_api, name='get_available_slots_api'),
    
    # Reservas
    path('reserva/<slug:salon_slug>/', views.booking_create, name='booking_create'),
    path('reserva/exito/<int:booking_id>/', views.booking_success, name='booking_success'),
    
    # Webhooks e Integraciones
    path('api/telegram/test/', views.test_telegram_integration, name='test_telegram'),
    path('api/webhooks/bold/<int:salon_slug>/', views.bold_webhook, name='bold_webhook_slug'), # Por si acaso
    path('api/webhooks/bold/<int:salon_id>/', views.bold_webhook, name='bold_webhook'),
]
