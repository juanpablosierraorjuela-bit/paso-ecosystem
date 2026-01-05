import os
import subprocess
import sys

# ==========================================
# 1. URLS MARKETPLACE (AÑADIR DETALLE NEGOCIO)
# ==========================================
marketplace_urls = """from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_home, name='home'),
    path('negocio/<int:business_id>/', views.business_detail, name='business_detail'),
]
"""

# ==========================================
# 2. VISTAS MARKETPLACE (LOGICA DEL DETALLE)
# ==========================================
marketplace_views = """from django.shortcuts import render, get_object_or_404
from apps.businesses.models import BusinessProfile

def marketplace_home(request):
    businesses = BusinessProfile.objects.all()
    return render(request, 'marketplace/index.html', {'businesses': businesses})

def business_detail(request, business_id):
    # Buscamos el negocio
    business = get_object_or_404(BusinessProfile, id=business_id)
    
    # Traemos sus servicios activos
    services = business.services.filter(is_active=True)
    
    # Traemos sus empleados (staff)
    employees = business.staff.filter(is_active=True)
    
    return render(request, 'marketplace/business_detail.html', {
        'business': business,
        'services': services,
        'employees': employees
    })
"""

# ==========================================
# 3. TEMPLATE MARKETPLACE (MEJORADO)
# ==========================================
marketplace_index_html = """{% extends 'base.html' %}
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

    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px;">
        {% for business in businesses %}
        <div class="business-card" style="background: #111; border-radius: 15px; overflow: hidden; border: 1px solid #333; transition: transform 0.3s ease; position: relative;">
            
            <div style="height: 140px; background: linear-gradient(135deg, #1a1a1a, #2c3e50); position: relative;">
                <span style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: #4cd137; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; border: 1px solid #4cd137; font-weight: bold;">
                    ● Abierto
                </span>
            </div>
            
            <div style="padding: 0 20px 20px; text-align: center; margin-top: -50px;">
                
                <div style="width: 90px; height: 90px; background: #d4af37; color: #000; font-size: 2.5rem; font-weight: bold; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin: 0 auto 15px; border: 5px solid #111; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
                    {{ business.business_name|first }}
                </div>
                
                <h3 style="color: white; margin-bottom: 5px; font-size: 1.3rem;">{{ business.business_name }}</h3>
                <p style="color: #888; font-size: 0.9rem; margin-bottom: 20px;">{{ business.address }}</p>
                
                <div style="display: flex; gap: 15px; justify-content: center; margin-bottom: 25px;">
                    {% if business.owner.instagram_link %}
                    <a href="{{ business.owner.instagram_link }}" target="_blank" title="Instagram" style="color: #ccc; font-size: 1.2rem; transition: color 0.3s;">
                        📷
                    </a>
                    {% endif %}
                    
                    {% if business.owner.phone %}
                    <a href="https://wa.me/{{ business.owner.phone }}" target="_blank" title="WhatsApp" style="color: #ccc; font-size: 1.2rem; transition: color 0.3s;">
                        💬
                    </a>
                    {% endif %}
                    
                    {% if business.google_maps_url %}
                    <a href="{{ business.google_maps_url }}" target="_blank" title="Ver en Mapa" style="color: #ccc; font-size: 1.2rem; transition: color 0.3s;">
                        📍
                    </a>
                    {% endif %}
                </div>
                
                <a href="{% url 'marketplace:business_detail' business.id %}" class="btn btn-outline" style="display: block; width: 100%; border-color: #d4af37; color: #d4af37; font-weight: bold; padding: 10px;">
                    Ver Servicios
                </a>
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
# 4. TEMPLATE DETALLE NEGOCIO (NUEVO)
# ==========================================
business_detail_html = """{% extends 'base.html' %}
{% block content %}
<div style="padding-top: 80px;">
    
    <div style="background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), #222; padding: 60px 5%; text-align: center; border-bottom: 1px solid #333;">
        <h1 style="color: #d4af37; font-size: 3rem; margin-bottom: 10px;">{{ business.business_name }}</h1>
        <p style="color: #ccc; font-size: 1.2rem; max-width: 600px; margin: 0 auto;">{{ business.description|default:"La excelencia en cada detalle." }}</p>
        
        <div style="margin-top: 20px; display: flex; gap: 20px; justify-content: center;">
            <span style="background: rgba(76, 209, 55, 0.2); color: #4cd137; padding: 5px 15px; border-radius: 20px; border: 1px solid #4cd137;">● Abierto Ahora</span>
            <span style="color: #888;">📍 {{ business.address }}</span>
        </div>
    </div>

    <div style="display: flex; max-width: 1200px; margin: 50px auto; gap: 50px; padding: 0 5%; flex-wrap: wrap;">
        
        <div style="flex: 2; min-width: 300px;">
            <h2 style="color: white; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 10px;">Nuestros Servicios</h2>
            
            <div style="display: flex; flex-direction: column; gap: 15px;">
                {% for service in services %}
                <div style="background: #111; padding: 20px; border-radius: 10px; border: 1px solid #333; display: flex; justify-content: space-between; align-items: center; transition: all 0.3s hover;">
                    <div>
                        <h3 style="color: white; font-size: 1.1rem; margin-bottom: 5px;">{{ service.name }}</h3>
                        <p style="color: #888; font-size: 0.9rem;">⏱ {{ service.duration_minutes }} min • {{ service.description|truncatechars:60 }}</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="color: #d4af37; font-weight: bold; font-size: 1.2rem; margin-bottom: 5px;">${{ service.price }}</p>
                        <button class="btn btn-primary" style="padding: 5px 15px; font-size: 0.8rem;">Reservar</button>
                    </div>
                </div>
                {% empty %}
                <p style="color: #666;">Este negocio aún no ha publicado sus servicios.</p>
                {% endfor %}
            </div>
        </div>

        <div style="flex: 1; min-width: 250px;">
            <h2 style="color: white; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 10px;">Especialistas</h2>
            
            <div style="display: grid; gap: 15px;">
                {% for employee in employees %}
                <div style="background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; display: flex; align-items: center; gap: 15px;">
                    <div style="width: 50px; height: 50px; background: #333; border-radius: 50%; overflow: hidden;">
                        {% if employee.profile_image %}
                            <img src="{{ employee.profile_image.url }}" style="width: 100%; height: 100%; object-fit: cover;">
                        {% else %}
                            <div style="width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; color: #888; font-weight: bold;">
                                {{ employee.first_name|first }}
                            </div>
                        {% endif %}
                    </div>
                    <div>
                        <h4 style="color: white; margin-bottom: 2px;">{{ employee.first_name }} {{ employee.last_name }}</h4>
                        <a href="#" style="color: #d4af37; font-size: 0.8rem; text-decoration: none;">Ver Portafolio</a>
                    </div>
                </div>
                {% empty %}
                <p style="color: #666;">No hay especialistas visibles.</p>
                {% endfor %}
            </div>
        </div>

    </div>
</div>
{% endblock %}
"""

# ==========================================
# 5. UTILIDADES
# ==========================================
def write_file(path, content):
    print(f"📝 Escribiendo: {path}...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error en {path}: {e}")

def run_command(command):
    print(f"🚀 Ejecutando: {command}")
    subprocess.run(command, shell=True, check=True)

def main():
    print("💎 PULIENDO MARKETPLACE Y CONECTANDO PÁGINA DE NEGOCIO 💎")
    
    # 1. URLs
    write_file('apps/marketplace/urls.py', marketplace_urls)
    
    # 2. Views
    write_file('apps/marketplace/views.py', marketplace_views)
    
    # 3. Templates
    write_file('templates/marketplace/index.html', marketplace_index_html)
    write_file('templates/marketplace/business_detail.html', business_detail_html)
    
    print("\n📦 Subiendo mejoras a Render...")
    try:
        run_command("git add .")
        run_command('git commit -m "Feat: Marketplace Mejorado y Detalle Negocio"')
        run_command("git push origin main")
        print("\n✅ ¡LISTO! Ahora el Marketplace se ve de lujo y los botones funcionan.")
    except Exception as e:
        print(f"⚠️ Error Git: {e}")
        
    try:
        os.remove(sys.argv[0])
    except:
        pass

if __name__ == "__main__":
    main()