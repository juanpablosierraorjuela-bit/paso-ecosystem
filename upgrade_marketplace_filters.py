import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ACTUALIZAR MARKETPLACE VIEWS (FILTROS)
# ==========================================
views_content = """
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta
from apps.businesses.models import Salon, Service
from apps.core.models import User
from apps.businesses.logic import AvailabilityManager
from apps.marketplace.models import Appointment
from apps.businesses.forms import COLOMBIA_CITIES # Importamos la lista oficial
import uuid

def home(request):
    # Obtener parámetros de búsqueda
    query = request.GET.get('q', '')
    city_filter = request.GET.get('city', '')

    # QuerySet base optimizado
    salons = Salon.objects.select_related('owner').all()

    # Aplicar filtros
    if query:
        salons = salons.filter(name__icontains=query)
    
    if city_filter:
        salons = salons.filter(city=city_filter)

    # Calcular estado abierto/cerrado solo para los resultados
    for salon in salons:
        salon.is_open_now = AvailabilityManager.is_salon_open(salon)
        
    # Extraer solo los nombres de las ciudades para el template
    city_list = [c[0] for c in COLOMBIA_CITIES]

    context = {
        'salons': salons,
        'cities': city_list,
        'current_city': city_filter,
        'current_query': query
    }
    return render(request, 'marketplace/index.html', context)

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    is_open = AvailabilityManager.is_salon_open(salon)
    services = salon.services.all()
    return render(request, 'marketplace/salon_detail.html', {
        'salon': salon, 'is_open': is_open, 'services': services
    })

def booking_wizard(request, salon_id, service_id):
    salon = get_object_or_404(Salon, pk=salon_id)
    service = get_object_or_404(Service, pk=service_id, salon=salon)
    employees = salon.employees.all()
    
    deposit_amount = int((service.price * salon.deposit_percentage) / 100)
    
    context = {
        'salon': salon,
        'service': service,
        'employees': employees,
        'deposit_amount': deposit_amount,
        'today': timezone.localtime(timezone.now()).strftime('%Y-%m-%d'),
        'is_guest': not request.user.is_authenticated
    }
    return render(request, 'marketplace/booking_wizard.html', context)

@require_GET
def get_available_slots_api(request):
    try:
        salon_id = request.GET.get('salon_id')
        service_id = request.GET.get('service_id')
        employee_id = request.GET.get('employee_id')
        date_str = request.GET.get('date')

        salon = get_object_or_404(Salon, pk=salon_id)
        service = get_object_or_404(Service, pk=service_id)
        employee = get_object_or_404(User, pk=employee_id)
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        slots = AvailabilityManager.get_available_slots(salon, service, employee, target_date)
        
        json_slots = []
        for slot in slots:
            json_slots.append({
                'time': slot['time_obj'].strftime('%H:%M'),
                'label': slot['label'],
                'available': slot['is_available']
            })
            
        return JsonResponse({'slots': json_slots})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def booking_commit(request):
    if request.method == 'POST':
        salon_id = request.POST.get('salon_id')
        service_id = request.POST.get('service_id')
        employee_id = request.POST.get('employee_id')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        salon = get_object_or_404(Salon, pk=salon_id)
        service = get_object_or_404(Service, pk=service_id)
        employee = get_object_or_404(User, pk=employee_id)
        
        booking_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        booking_datetime = timezone.make_aware(booking_datetime)
        deposit_val = (service.price * salon.deposit_percentage) / 100

        client_user = request.user

        if not client_user.is_authenticated:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Este correo ya está registrado. Por favor inicia sesión primero.")
                return redirect('login')
            
            temp_password = str(uuid.uuid4())[:8]
            
            client_user = User.objects.create_user(
                username=email,
                email=email,
                password=temp_password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='CLIENT',
                is_verified_payment=True
            )
            
            login(request, client_user)
            messages.success(request, f"¡Cuenta creada! Tu contraseña temporal es: {temp_password}")

        Appointment.objects.create(
            client=client_user,
            salon=salon,
            service=service,
            employee=employee,
            date_time=booking_datetime,
            total_price=service.price,
            deposit_amount=deposit_val,
            status='PENDING'
        )
        
        return redirect('client_dashboard')
        
    return redirect('marketplace_home')
"""

# ==========================================
# 2. ACTUALIZAR MARKETPLACE TEMPLATE (BARRA DE BUSQUEDA)
# ==========================================
html_index = """
{% extends 'base.html' %}

{% block content %}
<div class="bg-black text-white py-16 px-4">
    <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-4xl md:text-6xl font-serif mb-4 text-gold-500">
            Encuentra la Excelencia.
        </h1>
        <p class="text-gray-400 mb-8 text-lg">
            Los mejores expertos en belleza de Colombia, gestionados con Inteligencia.
        </p>
    </div>
</div>

<div class="container mx-auto px-4 py-12">
    
    <div class="bg-white p-6 rounded-xl shadow-lg -mt-20 relative z-10 border border-gray-100 max-w-5xl mx-auto">
        <form method="GET" action="{% url 'marketplace_home' %}" class="flex flex-col md:flex-row gap-4">
            
            <div class="flex-grow">
                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Buscar Negocio</label>
                <div class="relative">
                    <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                        🔍
                    </span>
                    <input type="text" name="q" value="{{ current_query }}" placeholder="Ej: Barbería El Patrón..." 
                           class="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 focus:ring-black focus:border-black transition">
                </div>
            </div>

            <div class="md:w-1/3">
                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Ciudad</label>
                <select name="city" onchange="this.form.submit()" 
                        class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-black focus:border-black bg-white transition cursor-pointer">
                    <option value="">Todas las Ciudades</option>
                    {% for city in cities %}
                        <option value="{{ city }}" {% if city == current_city %}selected{% endif %}>
                            {{ city }}
                        </option>
                    {% endfor %}
                </select>
            </div>

            <div class="md:w-auto flex items-end">
                <button type="submit" class="w-full bg-black text-white font-bold py-3 px-8 rounded-lg hover:bg-gray-800 transition shadow-lg h-[50px]">
                    Buscar
                </button>
            </div>
        </form>
    </div>

    <div class="mt-16">
        <h2 class="text-2xl font-serif text-gray-900 mb-8 flex items-center">
            Resultados
            {% if current_city %}
                <span class="ml-2 text-sm bg-gray-100 text-gray-600 px-3 py-1 rounded-full font-sans">en {{ current_city }}</span>
            {% endif %}
        </h2>

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
                        
                        <div class="flex space-x-3 items-center">
                            {% if salon.owner.phone %}
                            <a href="https://wa.me/57{{ salon.owner.phone }}" target="_blank" class="text-gray-400 hover:text-green-500 transition-colors" title="WhatsApp">
                                📱
                            </a>
                            {% endif %}

                            {% if salon.instagram_url %}
                            <a href="{{ salon.instagram_url }}" target="_blank" class="text-gray-400 hover:text-pink-600 transition-colors" title="Instagram">
                                📸
                            </a>
                            {% endif %}

                            {% if salon.google_maps_url %}
                            <a href="{{ salon.google_maps_url }}" target="_blank" class="text-gray-400 hover:text-blue-600 transition-colors" title="Ubicación">
                                📍
                            </a>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
            {% empty %}
            <div class="col-span-3 text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                <p class="text-gray-400 text-lg">No encontramos negocios con esos criterios.</p>
                <a href="{% url 'marketplace_home' %}" class="mt-4 inline-block text-black underline font-bold">Ver todos</a>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
"""

def apply_filters():
    print("🔍 IMPLEMENTANDO BUSCADOR Y FILTROS EN MARKETPLACE...")
    
    # 1. Views
    with open(BASE_DIR / 'apps' / 'marketplace' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(views_content.strip())
    print("✅ apps/marketplace/views.py: Filtros backend activados.")

    # 2. Template
    with open(BASE_DIR / 'templates' / 'marketplace' / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_index.strip())
    print("✅ templates/marketplace/index.html: Barra de búsqueda insertada.")

if __name__ == "__main__":
    apply_filters()