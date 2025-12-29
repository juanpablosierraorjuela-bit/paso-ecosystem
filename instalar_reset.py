import os

print("☢️  Instalando Botón de Reinicio Remoto...")

# 1. AGREGAR LA VISTA DE REINICIO A VIEWS.PY
views_path = os.path.join('apps', 'businesses', 'views.py')

with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Solo agregamos si no existe ya
if "def emergency_reset_db(request):" not in content:
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
    print("✅ Vista de reinicio agregada a views.py")

# 2. AGREGAR LA URL A URLS.PY
urls_path = os.path.join('apps', 'businesses', 'urls.py')

with open(urls_path, 'r', encoding='utf-8') as f:
    urls_content = f.read()

if "reset-database-secure-action" not in urls_content:
    # Insertamos la url antes del cierre de urlpatterns
    new_urls = urls_content.replace(
        "urlpatterns = [",
        "urlpatterns = [\n    path('reset-database-secure-action/', views.emergency_reset_db, name='emergency_reset'),"
    )
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(new_urls)
    print("✅ URL de reinicio agregada a urls.py")

print("\n🚀 LISTO. Ahora sigue estos pasos:")
print("1. Ejecuta: git add .")
print("2. Ejecuta: git commit -m 'Add emergency reset button'")
print("3. Ejecuta: git push origin main")
print("4. Espera a que Render termine el despliegue.")
print("5. Entra a: https://paso-backend.onrender.com/reset-database-secure-action/")
print("   (Debes estar logueado como Administrador)")