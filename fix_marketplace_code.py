import os
import sys

def rescatar_marketplace():
    print("🚑 RECONSTRUYENDO CÓDIGO DE MARKETPLACE...")

    # ==========================================
    # 1. ARREGLAR VIEWS.PY DE MARKETPLACE
    # ==========================================
    # Este archivo solía tener imports viejos. Lo haremos nuevo y limpio.
    views_path = os.path.join('apps', 'marketplace', 'views.py')
    
    views_content = """from django.shortcuts import render, redirect, get_object_or_404
from apps.businesses.models import Salon, Service, Booking
# Importamos la lógica de reserva que ya funciona en businesses
# para no duplicar código ni romper la base de datos.

def marketplace_home(request):
    # Buscador simple
    q = request.GET.get('q', '')
    city = request.GET.get('city', '')
    salons = Salon.objects.all()
    
    if q:
        salons = salons.filter(name__icontains=q)
    if city:
        salons = salons.filter(city=city)
        
    cities = Salon.objects.values_list('city', flat=True).distinct()
    return render(request, 'marketplace/index.html', {'salons': salons, 'cities': cities})

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    return render(request, 'marketplace/salon_detail.html', {'salon': salon})

def booking_create(request, service_id):
    # Redirige al wizard de businesses que ya está probado
    # Guardamos el servicio en sesión para iniciar el flujo
    request.session['booking_service'] = service_id
    service = get_object_or_404(Service, id=service_id)
    request.session['booking_salon'] = service.salon.id
    return redirect('booking_step_employee')

def booking_success(request, pk):
    return render(request, 'marketplace/booking_success.html')
"""
    
    os.makedirs(os.path.dirname(views_path), exist_ok=True)
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(views_content)
    print("✅ apps/marketplace/views.py reescrito correctamente.")

    # ==========================================
    # 2. ARREGLAR URLS.PY DE MARKETPLACE
    # ==========================================
    # Aseguramos que los nombres coincidan con las vistas de arriba
    urls_path = os.path.join('apps', 'marketplace', 'urls.py')
    
    urls_content = """from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace_home, name='home'),
    path('salon/<int:pk>/', views.salon_detail, name='salon_detail'),
    path('reservar/<int:service_id>/', views.booking_create, name='booking_create'),
    path('exito/<int:pk>/', views.booking_success, name='booking_success'),
]
"""
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content)
    print("✅ apps/marketplace/urls.py sincronizado.")

    # ==========================================
    # 3. ASEGURAR TEMPLATES BÁSICOS
    # ==========================================
    # Creamos carpetas y archivos dummy para que no falle por TemplateDoesNotExist
    base_tpl = os.path.join('templates', 'marketplace')
    os.makedirs(base_tpl, exist_ok=True)
    
    files = {
        'index.html': "{% extends 'master.html' %} {% block content %} <h1>Marketplace</h1> {% for s in salons %}<p>{{s.name}}</p>{% endfor %} {% endblock %}",
        'salon_detail.html': "{% extends 'master.html' %} {% block content %} <h1>{{ salon.name }}</h1> {% endblock %}",
        'booking_success.html': "{% extends 'master.html' %} {% block content %} <h1>¡Reserva Exitosa!</h1> {% endblock %}"
    }
    
    for fname, content in files.items():
        fpath = os.path.join(base_tpl, fname)
        if not os.path.exists(fpath):
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Template creado: {fname}")
        else:
            print(f"ℹ️ Template ya existe: {fname}")

    print("\n🚀 CÓDIGO DE MARKETPLACE REPARADO.")
    print("Sube esto a GitHub y el Error 500 debería desaparecer:")
    print("---------------------------------------------------")
    print("git add .")
    print("git commit -m \"Fix: Repair marketplace views and templates causing 500 error\"")
    print("git push origin main")
    print("---------------------------------------------------")

if __name__ == "__main__":
    rescatar_marketplace()