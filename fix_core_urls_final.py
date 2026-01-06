import os

# ==========================================
# CORRECCIÓN FINAL: APPS/CORE/URLS.PY
# ==========================================
core_urls_content = """from django.urls import path
from . import views

urlpatterns = [
    # Rutas simples y directas
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('soluciones-negocios/', views.pain_landing, name='pain_landing'),
    
    # AQUÍ ESTABA EL ERROR: Quitamos .as_view() porque ahora es una función
    path('registro-negocio/', views.OwnerRegisterView, name='register_owner'),
]
"""

def main():
    path = 'apps/core/urls.py'
    print(f"🔗 ACTUALIZANDO {path}...")
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(core_urls_content)
        print("✅ URLs de Core corregidas. ¡Adiós al AttributeError!")
        
        print("\n👉 EJECUTA ESTO PARA TERMINAR:")
        print("   1. python manage.py makemigrations")
        print("   2. python manage.py migrate")
        print("   3. git add .")
        print("   4. git commit -m 'Fix: Remove .as_view from core urls'")
        print("   5. git push origin main")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()