import os

# ESTE ES EL ARCHIVO URLS QUE INCLUYE 'MARKETPLACE' PARA QUE NO FALLE
contenido_urls_definitivo = r'''from django.urls import path
from . import views

urlpatterns = [
    # --- RUTAS PRINCIPALES (CON ALIAS PARA EVITAR ERRORES) ---
    path('', views.home, name='home'),
    path('marketplace/', views.home, name='marketplace'), # <--- ESTO ARREGLA EL ERROR DEL BOTÓN
    
    # --- USUARIOS ---
    path('registro-dueno/', views.register_owner, name='register_owner'),
    path('logout/', views.logout_view, name='logout'),
    
    # --- PANELES (DASHBOARDS) ---
    path('dashboard/admin/', views.owner_dashboard, name='admin_dashboard'),
    path('dashboard/cliente/', views.dashboard, name='dashboard'),
    path('dashboard/empleado/', views.employee_dashboard, name='employee_panel'),
    path('dashboard/empleado/eliminar-horario/', views.employee_dashboard, name='employee_delete_schedule'),
    
    # --- FUNCIONALIDADES ---
    path('servicio/eliminar/<int:service_id>/', views.delete_service, name='delete_service'),
    path('api/slots/', views.get_available_slots_api, name='get_available_slots_api'),
    
    # --- RESERVAS ---
    path('reserva/<slug:salon_slug>/', views.booking_create, name='booking_create'),
    path('reserva/exito/<int:booking_id>/', views.booking_success, name='booking_success'),
    
    # --- INTEGRACIONES ---
    path('api/telegram/test/', views.test_telegram_integration, name='test_telegram'),
    path('api/webhooks/bold/<int:salon_slug>/', views.bold_webhook, name='bold_webhook_slug'),
    path('api/webhooks/bold/<int:salon_id>/', views.bold_webhook, name='bold_webhook'),
]
'''

ruta_archivo = os.path.join('apps', 'businesses', 'urls.py')

print(f"🚑 Aplicando parche de emergencia en: {ruta_archivo}")

try:
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido_urls_definitivo)
    print("✅ ¡ARREGLADO! Se agregó la ruta 'marketplace' que faltaba.")
    print("👉 Por favor ejecuta: git add . && git commit -m 'fix marketplace url' && git push origin main")
except Exception as e:
    print(f"❌ Error escribiendo el archivo: {e}")