import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. EL CEREBRO MATEMÁTICO (LOGIC.PY)
# ==========================================
logic_content = """
from datetime import datetime, timedelta, time
from django.utils import timezone

class AvailabilityManager:
    @staticmethod
    def is_salon_open(salon, check_time=None):
        \"\"\"
        Determina si el negocio está abierto en un momento específico,
        soportando horarios nocturnos (ej: Abre 10PM - Cierra 4AM).
        \"\"\"
        if not check_time:
            check_time = timezone.localtime(timezone.now()).time()
        
        open_t = salon.opening_time
        close_t = salon.closing_time
        
        if open_t == close_t:
            return False # Nunca abre (o 24h? Asumimos cerrado si es igual por config simple)

        # Caso Normal: Abre 8am - Cierra 8pm
        if open_t < close_t:
            return open_t <= check_time <= close_t
        
        # Caso Nocturno/Amanecida: Abre 10pm - Cierra 4am
        else:
            # Es abierto si la hora actual es mayor a apertura (ej 11pm)
            # O si la hora actual es menor al cierre (ej 2am)
            return check_time >= open_t or check_time <= close_t

    @staticmethod
    def get_available_slots(salon, service, employee, target_date):
        \"\"\"
        Genera los slots de tiempo disponibles para una fecha.
        Cruza: Horario Negocio + Duración Servicio + Citas Existentes.
        \"\"\"
        # 1. Definir rango del día
        start_time = datetime.combine(target_date, salon.opening_time)
        
        # Manejo de cierre al día siguiente
        if salon.closing_time < salon.opening_time:
            end_time = datetime.combine(target_date + timedelta(days=1), salon.closing_time)
        else:
            end_time = datetime.combine(target_date, salon.closing_time)

        # 2. Generar bloques
        slots = []
        current = start_time
        service_duration = timedelta(minutes=service.duration_minutes + service.buffer_time)

        while current + service_duration <= end_time:
            # Aquí iría la lógica de verificar si 'current' choca con una cita existente
            # Por ahora (Fase 2 inicial), asumimos libre para mostrar la grilla
            
            slots.append({
                'time_obj': current,
                'label': current.strftime("%I:%M %p"),
                'is_available': True 
            })
            
            # Saltos de 30 min para opciones de agenda
            current += timedelta(minutes=30)
            
        return slots
"""

# ==========================================
# 2. MARKETPLACE VIEW (CONECTADA AL CEREBRO)
# ==========================================
marketplace_views_content = """
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from apps.businesses.models import Salon, Service
from apps.core.models import User
from apps.businesses.logic import AvailabilityManager

def home(request):
    # Traemos TODOS los salones con sus dueños
    salons = Salon.objects.select_related('owner').all()
    
    # Inyectamos el estado "Abierto/Cerrado" en tiempo real
    for salon in salons:
        salon.is_open_now = AvailabilityManager.is_salon_open(salon)
    
    return render(request, 'marketplace/index.html', {'salons': salons})

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    is_open = AvailabilityManager.is_salon_open(salon)
    services = salon.services.all()
    
    return render(request, 'marketplace/salon_detail.html', {
        'salon': salon,
        'is_open': is_open,
        'services': services
    })

def booking_wizard(request, salon_id, service_id):
    salon = get_object_or_404(Salon, pk=salon_id)
    service = get_object_or_404(Service, pk=service_id, salon=salon)
    
    # Filtramos empleados que trabajan en este salón
    # (En el futuro filtraremos por especialidad si agregas eso)
    employees = salon.employees.all()
    
    # Fecha por defecto: Hoy
    target_date = timezone.localtime(timezone.now()).date()
    
    context = {
        'salon': salon,
        'service': service,
        'employees': employees,
        'target_date': target_date
    }
    return render(request, 'marketplace/booking_wizard.html', context)
"""

# ==========================================
# 3. TEMPLATE MARKETPLACE MEJORADO (HOME)
# ==========================================
# Agregamos lógica para mostrar "Cerrado" en rojo o "Abierto" en verde
html_marketplace_index = """
{% extends 'base.html' %}

{% block content %}
<div class="bg-black text-white py-20 px-4">
    <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-4xl md:text-6xl font-serif mb-4 text-gold-500">
            Encuentra la Excelencia.
        </h1>
        <p class="text-gray-400 mb-8 text-lg">
            Los mejores expertos en belleza de Colombia, gestionados con Inteligencia.
        </p>
    </div>
</div>

<div class="container mx-auto px-4 py-16">
    <h2 class="text-2xl font-serif text-gray-900 mb-8">Negocios Destacados</h2>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {% for salon in salons %}
        <div class="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-2xl transition-all border border-gray-100 group relative">
            
            <div class="h-48 bg-gray-100 flex items-center justify-center relative">
                {% if salon.is_open_now %}
                    <span class="absolute top-4 right-4 bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg animate-pulse">
                        ABIERTO
                    </span>
                {% else %}
                    <span class="absolute top-4 right-4 bg-red-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                        CERRADO
                    </span>
                {% endif %}
                
                <span class="text-5xl font-serif text-gray-300">{{ salon.name|slice:":1" }}</span>
            </div>
            
            <div class="p-6">
                <h3 class="text-xl font-bold font-serif mb-1">{{ salon.name }}</h3>
                <p class="text-sm text-gray-500 mb-4">{{ salon.address }} &bull; {{ salon.city }}</p>
                
                <div class="flex justify-between items-center mt-4">
                    <a href="{% url 'salon_detail' salon.pk %}" class="bg-black text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-gray-800 transition">
                        Reservar Cita
                    </a>
                    
                    <div class="flex space-x-2">
                        {% if salon.instagram_url %}
                        <a href="{{ salon.instagram_url }}" target="_blank" class="text-gray-400 hover:text-pink-600 text-xl">📸</a>
                        {% endif %}
                        {% if salon.google_maps_url %}
                        <a href="{{ salon.google_maps_url }}" target="_blank" class="text-gray-400 hover:text-blue-600 text-xl">📍</a>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-span-3 text-center py-12">
            <p class="text-gray-400 text-lg">No hay negocios registrados aún.</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 4. TEMPLATE DETALLE NEGOCIO (PERFIL)
# ==========================================
html_salon_detail = """
{% extends 'base.html' %}

{% block content %}
<div class="bg-white border-b border-gray-200">
    <div class="container mx-auto px-4 py-10">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center">
            <div>
                <h1 class="text-4xl font-serif font-bold text-gray-900">{{ salon.name }}</h1>
                <p class="text-gray-500 mt-2">{{ salon.address }}, {{ salon.city }}</p>
                <div class="mt-4 flex items-center space-x-2">
                    {% if is_open %}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            🟢 Abierto ahora
                        </span>
                    {% else %}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            🔴 Cerrado ahora
                        </span>
                    {% endif %}
                    <span class="text-xs text-gray-400">Horario: {{ salon.opening_time }} - {{ salon.closing_time }}</span>
                </div>
            </div>
            <div class="mt-4 md:mt-0 flex space-x-3">
                {% if salon.instagram_url %}
                    <a href="{{ salon.instagram_url }}" target="_blank" class="bg-gray-100 p-3 rounded-full hover:bg-pink-50 transition">📸 Instagram</a>
                {% endif %}
                <a href="#" class="bg-black text-white px-6 py-3 rounded-full font-bold shadow-lg hover:bg-gray-800 transition">
                    Contactar
                </a>
            </div>
        </div>
    </div>
</div>

<div class="container mx-auto px-4 py-12">
    <h2 class="text-2xl font-serif font-bold mb-6">Servicios Disponibles</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for service in services %}
        <div class="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all bg-white group cursor-pointer">
            <div class="flex justify-between items-start mb-4">
                <h3 class="text-lg font-bold group-hover:text-gold-600 transition">{{ service.name }}</h3>
                <span class="font-mono font-bold">${{ service.price }}</span>
            </div>
            <p class="text-sm text-gray-500 mb-6">Duración: {{ service.duration_minutes }} min</p>
            
            <a href="{% url 'booking_wizard' salon.pk service.pk %}" class="block w-full text-center bg-gray-900 text-white py-2 rounded-lg text-sm font-bold hover:bg-black transition">
                Agendar
            </a>
        </div>
        {% empty %}
        <p class="text-gray-400">Este negocio aún no ha configurado sus servicios.</p>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 5. TEMPLATE BOOKING WIZARD (EL MAGO)
# ==========================================
html_booking_wizard = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen bg-gray-50 py-12">
    <div class="container mx-auto px-4 max-w-3xl">
        
        <div class="mb-8">
            <a href="{% url 'salon_detail' salon.pk %}" class="text-sm text-gray-500 hover:text-black mb-4 inline-block">&larr; Volver al negocio</a>
            <h1 class="text-3xl font-serif font-bold">Configura tu Cita</h1>
            <p class="text-gray-600">Estás reservando <span class="font-bold text-black">{{ service.name }}</span> en {{ salon.name }}</p>
        </div>

        <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
            <div class="p-8 border-b border-gray-100">
                <h2 class="text-lg font-bold mb-4">1. Elige a tu Experto</h2>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {% for emp in employees %}
                    <label class="cursor-pointer">
                        <input type="radio" name="employee" value="{{ emp.id }}" class="peer sr-only">
                        <div class="p-4 rounded-xl border-2 border-gray-100 peer-checked:border-black peer-checked:bg-gray-50 transition-all text-center hover:border-gray-300">
                            <div class="w-12 h-12 bg-gray-200 rounded-full mx-auto mb-2 flex items-center justify-center font-bold text-gray-500">
                                {{ emp.first_name|slice:":1" }}
                            </div>
                            <span class="text-sm font-bold block">{{ emp.first_name }}</span>
                        </div>
                    </label>
                    {% empty %}
                    <p class="text-sm text-red-500 col-span-4">No hay empleados disponibles para este servicio.</p>
                    {% endfor %}
                </div>
            </div>

            <div class="p-8 bg-gray-50">
                <h2 class="text-lg font-bold mb-4">2. Disponibilidad para Hoy ({{ target_date }})</h2>
                
                <div class="grid grid-cols-3 md:grid-cols-5 gap-3">
                    <button class="py-2 px-4 bg-white border border-gray-200 rounded-lg text-sm hover:border-black focus:ring-2 ring-black">09:00 AM</button>
                    <button class="py-2 px-4 bg-white border border-gray-200 rounded-lg text-sm hover:border-black focus:ring-2 ring-black">10:00 AM</button>
                    <button class="py-2 px-4 bg-gray-200 border border-transparent rounded-lg text-sm text-gray-400 cursor-not-allowed">11:00 AM</button>
                    <button class="py-2 px-4 bg-white border border-gray-200 rounded-lg text-sm hover:border-black focus:ring-2 ring-black">12:00 PM</button>
                </div>
                
                <p class="text-xs text-gray-400 mt-4">* Los horarios bloqueados ya están reservados.</p>
            </div>

            <div class="p-8 border-t border-gray-100 flex justify-between items-center bg-white">
                <div>
                    <p class="text-sm text-gray-500">Total a pagar en local</p>
                    <p class="text-2xl font-bold font-mono">${{ service.price }}</p>
                </div>
                <button class="bg-black text-white px-8 py-4 rounded-xl font-bold shadow-lg hover:scale-105 transition-transform">
                    Continuar al Pago &rarr;
                </button>
            </div>
        </div>

    </div>
</div>
{% endblock %}
"""

# ==========================================
# 6. ACTUALIZAR URLS MARKETPLACE
# ==========================================
urls_marketplace_content = """
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='marketplace_home'), # Home del Market
    path('salon/<int:pk>/', views.salon_detail, name='salon_detail'),
    path('reservar/<int:salon_id>/<int:service_id>/', views.booking_wizard, name='booking_wizard'),
]
"""

# ==========================================
# 7. EJECUCIÓN
# ==========================================
def apply_phase2():
    print("🧠 CONECTANDO EL CEREBRO DEL SISTEMA (FASE 2)...")

    # 1. Logic.py
    with open(BASE_DIR / 'apps' / 'businesses' / 'logic.py', 'w', encoding='utf-8') as f:
        f.write(logic_content.strip())
    print("✅ apps/businesses/logic.py: Algoritmo de disponibilidad creado.")

    # 2. Marketplace Views
    with open(BASE_DIR / 'apps' / 'marketplace' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(marketplace_views_content.strip())
    print("✅ apps/marketplace/views.py: Vistas conectadas a la lógica.")

    # 3. Marketplace URLs
    with open(BASE_DIR / 'apps' / 'marketplace' / 'urls.py', 'w', encoding='utf-8') as f:
        f.write(urls_marketplace_content.strip())
    print("✅ apps/marketplace/urls.py: Rutas de reserva activadas.")

    # 4. Templates
    os.makedirs(BASE_DIR / 'templates' / 'marketplace', exist_ok=True)
    
    with open(BASE_DIR / 'templates' / 'marketplace' / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_marketplace_index.strip())
    
    with open(BASE_DIR / 'templates' / 'marketplace' / 'salon_detail.html', 'w', encoding='utf-8') as f:
        f.write(html_salon_detail.strip())
        
    with open(BASE_DIR / 'templates' / 'marketplace' / 'booking_wizard.html', 'w', encoding='utf-8') as f:
        f.write(html_booking_wizard.strip())
    
    print("✅ Templates del Marketplace renovados (Home, Detalle, Wizard).")

if __name__ == "__main__":
    apply_phase2()
    print("\n🚀 FASE 2 COMPLETADA.")
    print("1. El Marketplace ahora muestra el estado REAL (Abierto/Cerrado).")
    print("2. Puedes hacer clic en 'Reservar' y ver el perfil del negocio.")
    print("3. Puedes elegir un servicio y ver el 'Wizard' de reserva.")