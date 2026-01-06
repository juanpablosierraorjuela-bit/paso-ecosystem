import os

# ==========================================
# 1. ACTUALIZAR URLS (ROUTING)
# ==========================================
urls_content = """from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('services/', views.services_list, name='services'),
    path('schedule/', views.schedule_list, name='schedule'),
    # RUTAS NUEVAS AGREGADAS POR EL SCRIPT MÁGICO
    path('panel/', views.panel_negocio, name='panel_negocio'),
]
"""

# ==========================================
# 2. CREAR EL TEMPLATE (FRONTEND)
# ==========================================
panel_html = """{% extends 'base.html' %}

{% block content %}
<div style="padding: 100px 5%; text-align: center; background-color: #000; min-height: 80vh; color: white;">
    
    <div style="margin-bottom: 40px;">
        <h1 style="font-size: 3rem; color: #d4af37; margin-bottom: 10px;">¡Panel de Control Activo! 🚀</h1>
        <p style="color: #888; font-size: 1.2rem;">Bienvenido a tu centro de mando, {{ user.first_name }}.</p>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; max-width: 1000px; margin: 0 auto;">
        <div style="background: #111; padding: 30px; border-radius: 15px; border: 1px solid #333;">
            <h3 style="color: white; margin-bottom: 15px;">📅 Mis Citas</h3>
            <p style="color: #666; font-size: 0.9rem;">Gestiona tu agenda y verifíca los pagos.</p>
            <button class="btn btn-outline" style="width: 100%; margin-top: 20px; border-color: #d4af37; color: #d4af37;">Ver Agenda</button>
        </div>

        <div style="background: #111; padding: 30px; border-radius: 15px; border: 1px solid #333;">
            <h3 style="color: white; margin-bottom: 15px;">✂️ Servicios</h3>
            <p style="color: #666; font-size: 0.9rem;">Configura precios y duración.</p>
            <a href="{% url 'businesses:services' %}" class="btn btn-primary" style="display: block; width: 100%; margin-top: 20px;">Administrar</a>
        </div>

        <div style="background: #111; padding: 30px; border-radius: 15px; border: 1px solid #333;">
            <h3 style="color: white; margin-bottom: 15px;">👥 Equipo</h3>
            <p style="color: #666; font-size: 0.9rem;">Gestiona tus empleados y perfiles.</p>
            <button class="btn btn-outline" style="width: 100%; margin-top: 20px; border-color: white; color: white;">Ver Staff</button>
        </div>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 3. LÓGICA DE INYECCIÓN (BACKEND)
# ==========================================
def inject_view():
    views_path = 'apps/businesses/views.py'
    
    # Leemos el archivo actual
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Código de la vista a inyectar
    new_view = """

@login_required
def panel_negocio(request):
    # Vista simple para renderizar el panel nuevo
    return render(request, 'negocio/panel.html')
"""
    
    if "def panel_negocio(request):" not in content:
        print("💉 Inyectando vista 'panel_negocio' en views.py...")
        with open(views_path, 'a', encoding='utf-8') as f:
            f.write(new_view)
    else:
        print("✅ La vista 'panel_negocio' ya existía.")

def write_file(path, content):
    print(f"📝 Escribiendo archivo: {path}...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error escribiendo {path}: {e}")

# ==========================================
# EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    print("🪄 INICIANDO MAGIA DE REPARACIÓN 404 🪄")
    
    # 1. Inyectar la Lógica
    inject_view()
    
    # 2. Corregir las URLs
    write_file('apps/businesses/urls.py', urls_content)
    
    # 3. Crear el Template
    write_file('templates/negocio/panel.html', panel_html)
    
    print("\n✅ ¡LISTO! El error 404 debería haber desaparecido.")
    print("👉 Ejecuta estos comandos para subir los cambios a Render:")
    print("   git add .")
    print('   git commit -m "Fix: Error 404 en Negocio Panel"')
    print("   git push origin main")