import os

# 1. CONTENIDO PARA APPS/BUSINESSES/URLS.PY
# Este archivo conecta tus funciones (vistas) con direcciones web reales.
contenido_businesses_urls = r'''from django.urls import path
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
'''

# 2. CONTENIDO PARA CONFIG/URLS.PY
# Este es el "mapa maestro" que incluye las URLs de tu aplicación.
contenido_config_urls = r'''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Conectamos las URLs de la app businesses a la raíz del sitio
    path('', include('apps.businesses.urls')),
]

# Soporte para archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''

# --- EJECUCIÓN DEL ARREGLO ---
print("🛠️ Iniciando reparación de URLs...")

# Ruta 1: apps/businesses/urls.py
ruta_businesses = os.path.join('apps', 'businesses', 'urls.py')
try:
    with open(ruta_businesses, 'w', encoding='utf-8') as f:
        f.write(contenido_businesses_urls)
    print(f"✅ Archivo creado/corregido: {ruta_businesses}")
except Exception as e:
    print(f"❌ Error escribiendo {ruta_businesses}: {e}")

# Ruta 2: config/urls.py
ruta_config = os.path.join('config', 'urls.py')
try:
    with open(ruta_config, 'w', encoding='utf-8') as f:
        f.write(contenido_config_urls)
    print(f"✅ Archivo maestro corregido: {ruta_config}")
except Exception as e:
    print(f"❌ Error escribiendo {ruta_config}: {e}")

print("\n✨ ¡LISTO! Las URLs han sido conectadas.")
print("👉 Ejecuta ahora: git add . && git commit -m 'Fix URLs' && git push origin main")