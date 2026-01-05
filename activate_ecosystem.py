import os

# ==========================================
# 1. MARKETPLACE: CONECTAR A LA BASE DE DATOS
# ==========================================
# Ahora la vista busca TODOS los negocios registrados
marketplace_views = """from django.shortcuts import render
from apps.businesses.models import BusinessProfile
from django.utils import timezone

def marketplace_home(request):
    # Traemos todos los negocios del sistema
    businesses = BusinessProfile.objects.all()
    
    # Aquí podríamos agregar lógica de filtros por ciudad más adelante
    return render(request, 'marketplace/index.html', {'businesses': businesses})
"""

# Template del Marketplace con Tarjetas de Lujo
marketplace_template = """{% extends 'base.html' %}
{% load static %}

{% block content %}
<div style="background-color: #000; min-height: 100vh; padding: 100px 5% 50px;">
    
    <div style="text-align: center; margin-bottom: 50px;">
        <h1 style="font-size: 3rem; color: #d4af37; margin-bottom: 10px;">Marketplace PASO</h1>
        <p style="color: #888; font-size: 1.2rem;">Encuentra la excelencia cerca de ti.</p>
        
        <div style="margin-top: 30px; display: inline-flex; background: #111; border: 1px solid #333; border-radius: 50px; padding: 5px 20px 5px 5px; width: 100%; max-width: 600px;">
            <input type="text" placeholder="¿Qué servicio buscas hoy?" style="background: transparent; border: none; color: white; padding: 10px; flex: 1; outline: none;">
            <button class="btn btn-primary" style="border-radius: 40px; padding: 10px 30px;">Buscar</button>
        </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 30px;">
        {% for business in businesses %}
        <div class="business-card" style="background: #111; border-radius: 15px; overflow: hidden; border: 1px solid #333; transition: transform 0.3s ease;">
            
            <div style="height: 150px; background: linear-gradient(45deg, #222, #333); position: relative;">
                <span style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: #4cd137; padding: 5px 10px; border-radius: 20px; font-size: 0.8rem; border: 1px solid #4cd137;">
                    ● Abierto
                </span>
            </div>
            
            <div style="padding: 20px; text-align: center; margin-top: -40px;">
                <div style="width: 80px; height: 80px; background: #d4af37; color: black; font-size: 2rem; font-weight: bold; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin: 0 auto 15px; border: 4px solid #111;">
                    {{ business.business_name|first }}
                </div>
                
                <h3 style="color: white; margin-bottom: 5px;">{{ business.business_name }}</h3>
                <p style="color: #888; font-size: 0.9rem; margin-bottom: 15px;">{{ business.address }}</p>
                
                <div style="display: flex; gap: 10px; justify-content: center; margin-bottom: 20px;">
                    <a href="#" class="btn-icon" style="color: #ccc; text-decoration: none;">📷 Instagram</a>
                    <a href="#" class="btn-icon" style="color: #ccc; text-decoration: none;">📍 Mapa</a>
                </div>
                
                <button class="btn btn-outline" style="width: 100%; border-color: #d4af37; color: #d4af37;">Ver Servicios</button>
            </div>
        </div>
        {% empty %}
        <div style="grid-column: 1/-1; text-align: center; padding: 50px;">
            <h3 style="color: #666;">Aún no hay unicornios en esta zona.</h3>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 2. PANEL EMPLEADO: MOSTRAR CITAS REALES
# ==========================================
# La vista ahora filtra citas VERIFICADAS del usuario logueado
booking_views = """from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Appointment

@login_required
def employee_dashboard(request):
    # Buscamos citas donde el empleado sea el usuario actual
    # Y que estén VERIFICADAS (pagas)
    appointments = Appointment.objects.filter(
        employee=request.user,
        status='VERIFIED'
    ).order_by('date', 'start_time')
    
    return render(request, 'booking/employee_dashboard.html', {'appointments': appointments})

@login_required
def client_dashboard(request):
    return render(request, 'booking/client_dashboard.html')
"""

# Template del Panel de Empleado
employee_template = """{% extends 'base.html' %}
{% block content %}
<div style="padding: 100px 5%; color: white;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <div>
            <h1 style="color: #d4af37;">Hola, {{ user.first_name }}</h1>
            <p style="color: #ccc;">Tu agenda de trabajo para hoy.</p>
        </div>
        <div style="background: #222; padding: 10px 20px; border-radius: 10px;">
            <span style="color: #888;">Estado:</span> <span style="color: #4cd137;">● Activo</span>
        </div>
    </div>

    <div style="display: grid; gap: 20px;">
        {% for cita in appointments %}
        <div style="background: #111; border-left: 4px solid #d4af37; padding: 20px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="font-size: 1.2rem; margin-bottom: 5px;">{{ cita.service.name }}</h3>
                <p style="color: #888;">Cliente: <strong style="color: white;">{{ cita.client.first_name }} {{ cita.client.last_name }}</strong></p>
                <p style="color: #888;">Hora: <strong style="color: #d4af37;">{{ cita.start_time|time:"H:i" }} - {{ cita.end_time|time:"H:i" }}</strong></p>
            </div>
            <div>
                <a href="#" class="btn btn-outline" style="font-size: 0.8rem;">Ver Detalles</a>
            </div>
        </div>
        {% empty %}
        <div style="text-align: center; padding: 50px; background: #111; border-radius: 10px; border: 1px dashed #333;">
            <h3 style="color: #666;">Todo tranquilo por ahora.</h3>
            <p style="color: #444;">No tienes citas verificadas asignadas.</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 3. FUNCIÓN DE ESCRITURA
# ==========================================
def write_file(path, content):
    print(f"📝 Actualizando: {path}...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error escribiendo {path}: {e}")

def main():
    print("🚀 ACTIVANDO MARKETPLACE Y PANEL DE EMPLEADO...")
    
    # 1. Marketplace
    write_file('apps/marketplace/views.py', marketplace_views)
    write_file('templates/marketplace/index.html', marketplace_template)
    
    # 2. Panel Empleado
    write_file('apps/booking/views.py', booking_views)
    write_file('templates/booking/employee_dashboard.html', employee_template)
    
    print("\n✅ Archivos generados correctamente.")
    print("👉 EJECUTA ESTO AHORA EN TU TERMINAL:")
    print("   git add .")
    print('   git commit -m "Feat: Marketplace Dinamico y Agenda Empleado"')
    print("   git push origin main")

if __name__ == "__main__":
    main()