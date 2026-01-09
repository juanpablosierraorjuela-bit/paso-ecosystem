import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ENSEÑARLE EL CAMINO A DJANGO (SETTINGS)
# ==========================================
def fix_settings():
    settings_path = BASE_DIR / 'config' / 'settings.py'
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Le decimos a Django: "Cuando alguien entre, pregúntale a la vista 'dispatch' adónde ir"
    if 'LOGIN_REDIRECT_URL' not in content:
        redirect_settings = """
# --- REDIRECCIÓN INTELIGENTE ---
LOGIN_REDIRECT_URL = 'dispatch'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'
"""
        with open(settings_path, 'a', encoding='utf-8') as f:
            f.write(redirect_settings)
        print("✅ settings.py: Redirección configurada.")
    else:
        print("ℹ️ settings.py ya tenía configuración.")

# ==========================================
# 2. CREAR EL SEMÁFORO (VIEWS.PY)
# ==========================================
def fix_views():
    views_path = BASE_DIR / 'apps' / 'core' / 'views.py'
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Esta lógica respeta estrictamente los ROLES de la Biblia
    dispatch_logic = """

# --- SEMÁFORO DE BIENVENIDA ---
from django.contrib.auth.decorators import login_required

@login_required
def dispatch_user(request):
    user = request.user
    
    # 1. Si es Dueño -> Panel de Negocio (Ruta 'dashboard' de businesses)
    if user.role == 'OWNER':
        return redirect('dashboard')
    
    # 2. Si es Cliente -> Marketplace (Ruta 'marketplace_home' de marketplace)
    elif user.role == 'CLIENT':
        return redirect('marketplace_home')
        
    # 3. Si es Empleado -> Su Agenda (Ruta actual de lista de empleados)
    # Nota: Cuando creemos el dashboard de empleado en Fase 3, cambiaremos esto a 'employee_dashboard'
    elif user.role == 'EMPLOYEE':
        return redirect('employees_list')
        
    # 4. Si eres TÚ (Superuser) -> Admin de Django
    elif user.is_superuser:
        return redirect('/admin/')
        
    else:
        return redirect('home')
"""

    if 'def dispatch_user' not in content:
        with open(views_path, 'a', encoding='utf-8') as f:
            f.write(dispatch_logic)
        print("✅ apps/core/views.py: Semáforo creado.")

# ==========================================
# 3. CREAR LA RUTA (URLS.PY)
# ==========================================
def fix_urls():
    urls_path = BASE_DIR / 'apps' / 'core' / 'urls.py'
    
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "name='dispatch'" not in content:
        # Inyectamos la URL 'ingreso-exitoso' que usa el settings
        # No borra nada, solo agrega una línea al urlpatterns
        new_pattern = "    path('ingreso-exitoso/', views.dispatch_user, name='dispatch'),"
        content = content.replace(
            "urlpatterns = [",
            f"urlpatterns = [\n{new_pattern}"
        )
        
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ apps/core/urls.py: Ruta conectada.")

if __name__ == "__main__":
    fix_settings()
    fix_views()
    fix_urls()
    print("🚀 LISTO. Ahora al iniciar sesión, irán directo a su destino.")