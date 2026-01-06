import os

# ==========================================
# NUEVO CONTENIDO PARA APPS/CORE/VIEWS.PY
# ==========================================
core_views_content = """from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# Importamos el modelo correcto (Salon)
from apps.businesses.models import Salon 

def home(request):
    return render(request, 'home.html')

def pain_landing(request):
    # Landing page simple
    return render(request, 'landing/pain_points.html')

@login_required
def dashboard_redirect(request):
    # Esta vista decide a dónde enviar al usuario cuando entra
    user = request.user
    
    if user.role == 'OWNER':
        # Redirigir al dashboard del dueño (en la app businesses)
        return redirect('businesses:owner_dashboard')
        
    elif user.role == 'EMPLOYEE':
        # Redirigir al dashboard del empleado
        return redirect('businesses:employee_dashboard')
        
    else:
        # Si es cliente o admin, al home por ahora
        return redirect('home')

def OwnerRegisterView(request):
    # Si alguien intenta usar la url vieja de registro,
    # lo mandamos a la nueva que sí funciona.
    return redirect('businesses:register_owner')
"""

def main():
    path = 'apps/core/views.py'
    print(f"🚑 REESCRIBIENDO {path} PARA ELIMINAR ERRORES...")
    
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(core_views_content)
        print("✅ Archivo core/views.py reparado y compatible con Salon.")
        
        print("\n👉 EJECUTA AHORA EN ORDEN:")
        print("   1. python manage.py makemigrations")
        print("   2. python manage.py migrate")
        print("   3. git add .")
        print("   4. git commit -m 'Fix: Core views compatible with Salon'")
        print("   5. git push origin main")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()