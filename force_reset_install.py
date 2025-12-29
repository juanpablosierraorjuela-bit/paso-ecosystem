import os

print("☢️  Forzando instalación del Botón de Reinicio...")

# 1. ASEGURAR VIEWS.PY (Agregamos la función si falta)
views_path = os.path.join('apps', 'businesses', 'views.py')

try:
    with open(views_path, 'r', encoding='utf-8') as f:
        views_content = f.read()

    # Solo agregamos el código si no lo vemos dentro del archivo
    if "def emergency_reset_db(request):" not in views_content:
        print("   ⚠️ La función no estaba en views.py. Agregándola...")
        reset_code = """

# --- ZONA DE PELIGRO: REINICIO DE FÁBRICA ---
@csrf_exempt
def emergency_reset_db(request):
    if not request.user.is_superuser:
        return HttpResponse("⛔ ACCESO DENEGADO. Solo el Dueño del SaaS puede hacer esto.", status=403)
    
    try:
        # 1. Borrar Reservas
        Booking.objects.all().delete()
        # 2. Borrar Horarios
        EmployeeSchedule.objects.all().delete()
        # 3. Borrar Servicios
        Service.objects.all().delete()
        # 4. Borrar Salones
        Salon.objects.all().delete()
        # 5. Borrar Usuarios (Menos Tú)
        User.objects.filter(is_superuser=False).delete()
        
        return HttpResponse("✅ ¡SISTEMA LIMPIO! Base de datos reiniciada a 0 km.", status=200)
    except Exception as e:
        return HttpResponse(f"❌ Error: {str(e)}", status=500)
"""
        with open(views_path, 'a', encoding='utf-8') as f:
            f.write(reset_code)
    else:
        print("   ✅ La función ya existe en views.py.")

except Exception as e:
    print(f"❌ Error leyendo views.py: {e}")


# 2. REESCRIBIR URLS.PY COMPLETO (Para evitar errores de inserción)
urls_path = os.path.join('apps', 'businesses', 'urls.py')

# Este es el contenido COMPLETO y CORRECTO del archivo
new_urls_content = """from django.urls import path
from . import views

urlpatterns = [
    # --- BOTÓN DE PÁNICO (Solo Admin) ---
    path('reset-database-secure-action/', views.emergency_reset_db, name='emergency_reset'),

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
"""

try:
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(new_urls_content)
    print("✅ urls.py reescrito exitosamente con la ruta de reinicio.")

except Exception as e:
    print(f"❌ Error escribiendo urls.py: {e}")

print("\n🚀 LISTO. Ahora haz el deploy de nuevo:")
print("1. git add .")
print("2. git commit -m 'Force add reset url'")
print("3. git push origin main")