import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ACTUALIZAR MARKETPLACE VIEWS (API + GUARDADO)
# ==========================================
marketplace_views = """
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import datetime, timedelta
from apps.businesses.models import Salon, Service
from apps.core.models import User
from apps.businesses.logic import AvailabilityManager
from apps.marketplace.models import Appointment

def home(request):
    salons = Salon.objects.select_related('owner').all()
    for salon in salons:
        salon.is_open_now = AvailabilityManager.is_salon_open(salon)
    return render(request, 'marketplace/index.html', {'salons': salons})

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    is_open = AvailabilityManager.is_salon_open(salon)
    services = salon.services.all()
    return render(request, 'marketplace/salon_detail.html', {
        'salon': salon, 'is_open': is_open, 'services': services
    })

# --- WIZARD VISUAL ---
@login_required
def booking_wizard(request, salon_id, service_id):
    salon = get_object_or_404(Salon, pk=salon_id)
    service = get_object_or_404(Service, pk=service_id, salon=salon)
    employees = salon.employees.all() # En futuro filtrar por capacidad
    
    # Calcular abono
    deposit_amount = (service.price * salon.deposit_percentage) / 100
    
    context = {
        'salon': salon,
        'service': service,
        'employees': employees,
        'deposit_amount': deposit_amount,
        'today': timezone.localtime(timezone.now()).strftime('%Y-%m-%d')
    }
    return render(request, 'marketplace/booking_wizard.html', context)

# --- API: OBTENER HORAS DISPONIBLES (AJAX) ---
@require_GET
@login_required
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
        
        # USAMOS EL CEREBRO LOGIC.PY
        slots = AvailabilityManager.get_available_slots(salon, service, employee, target_date)
        
        # Convertir a formato JSON simple
        json_slots = []
        for slot in slots:
            json_slots.append({
                'time': slot['time_obj'].strftime('%H:%M'), # 14:30
                'label': slot['label'],                     # 02:30 PM
                'available': slot['is_available']
            })
            
        return JsonResponse({'slots': json_slots})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --- CONFIRMAR RESERVA ---
@login_required
def booking_commit(request):
    if request.method == 'POST':
        salon_id = request.POST.get('salon_id')
        service_id = request.POST.get('service_id')
        employee_id = request.POST.get('employee_id')
        date_str = request.POST.get('date') # YYYY-MM-DD
        time_str = request.POST.get('time') # HH:MM

        salon = get_object_or_404(Salon, pk=salon_id)
        service = get_object_or_404(Service, pk=service_id)
        employee = get_object_or_404(User, pk=employee_id)
        
        # Crear fecha completa
        booking_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        # Hacerla timezone aware
        booking_datetime = timezone.make_aware(booking_datetime)

        deposit_val = (service.price * salon.deposit_percentage) / 100

        # CREAR CITA
        appointment = Appointment.objects.create(
            client=request.user,
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
# 2. ACTUALIZAR MARKETPLACE URLS
# ==========================================
marketplace_urls = """
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='marketplace_home'),
    path('salon/<int:pk>/', views.salon_detail, name='salon_detail'),
    path('reservar/<int:salon_id>/<int:service_id>/', views.booking_wizard, name='booking_wizard'),
    
    # Rutas Nuevas
    path('api/slots/', views.get_available_slots_api, name='api_get_slots'),
    path('reservar/confirmar/', views.booking_commit, name='booking_commit'),
]
"""

# ==========================================
# 3. CLIENT DASHBOARD VIEW (APPS/CORE/VIEWS.PY)
# ==========================================
# Agregaremos la vista client_dashboard al final de core/views.py
def update_core_views():
    path = BASE_DIR / 'apps' / 'core' / 'views.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "def client_dashboard" not in content:
        # Import necesario para Appointment
        imports = "from apps.marketplace.models import Appointment\nimport re\n"
        content = imports + content
        
        new_view = """
# --- PANEL CLIENTE ---
@login_required
def client_dashboard(request):
    if request.user.role != 'CLIENT':
        return redirect('dispatch')
        
    appointments = Appointment.objects.filter(client=request.user).order_by('-created_at')
    
    # Procesar lógica de WhatsApp para cada cita
    for app in appointments:
        if app.status == 'PENDING':
            # Calcular tiempo restante (60 min)
            elapsed = timezone.now() - app.created_at
            remaining = timedelta(minutes=60) - elapsed
            app.seconds_left = max(0, int(remaining.total_seconds()))
            
            # Link WhatsApp
            owner_phone = app.salon.owner.phone
            clean_phone = re.sub(r'\D', '', str(owner_phone)) if owner_phone else '573000000000'
            
            msg = (
                f"Hola {app.salon.name}, soy {request.user.first_name}. "
                f"Confirmo mi cita para {app.service.name} el {app.date_time.strftime('%d/%m %I:%M %p')}. "
                f"Adjunto abono de ${int(app.deposit_amount)}."
            )
            app.wa_link = f"https://wa.me/{clean_phone}?text={msg}"
            
    return render(request, 'core/client_dashboard.html', {'appointments': appointments})
"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content + new_view)
            
# ==========================================
# 4. ACTUALIZAR CORE URLS (CLIENT DASHBOARD)
# ==========================================
def update_core_urls():
    path = BASE_DIR / 'apps' / 'core' / 'urls.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "name='client_dashboard'" not in content:
        new_pattern = "    path('mi-perfil/', views.client_dashboard, name='client_dashboard'),"
        content = content.replace("urlpatterns = [", f"urlpatterns = [\n{new_pattern}")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

# ==========================================
# 5. TEMPLATE WIZARD CON JAVASCRIPT (EL CEREBRO EN FRONTEND)
# ==========================================
html_wizard_js = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen bg-gray-50 py-12">
    <div class="container mx-auto px-4 max-w-3xl">
        
        <div class="mb-8">
            <a href="{% url 'salon_detail' salon.pk %}" class="text-sm text-gray-500 hover:text-black mb-4 inline-block">&larr; Volver</a>
            <h1 class="text-3xl font-serif font-bold">Reserva tu experiencia</h1>
            <p class="text-gray-600">Servicio: <strong>{{ service.name }}</strong> (${{ service.price }})</p>
        </div>

        <form action="{% url 'booking_commit' %}" method="POST" id="bookingForm">
            {% csrf_token %}
            <input type="hidden" name="salon_id" value="{{ salon.id }}">
            <input type="hidden" name="service_id" value="{{ service.id }}">
            <input type="hidden" name="employee_id" id="selectedEmployee">
            <input type="hidden" name="time" id="selectedTime">

            <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
                
                <div class="p-8 border-b border-gray-100">
                    <h2 class="text-lg font-bold mb-4">1. Elige Especialista</h2>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {% for emp in employees %}
                        <label class="cursor-pointer group">
                            <input type="radio" name="employee_radio" value="{{ emp.id }}" class="peer sr-only" onchange="selectEmployee(this)">
                            <div class="p-4 rounded-xl border-2 border-gray-100 peer-checked:border-black peer-checked:bg-gray-50 transition-all text-center hover:border-gray-300">
                                <div class="w-12 h-12 bg-gray-200 rounded-full mx-auto mb-2 flex items-center justify-center font-bold text-gray-500">
                                    {{ emp.first_name|slice:":1" }}
                                </div>
                                <span class="text-sm font-bold block">{{ emp.first_name }}</span>
                            </div>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <div class="p-8 bg-gray-50 transition-opacity duration-300 opacity-50 pointer-events-none" id="step2">
                    <h2 class="text-lg font-bold mb-4">2. Selecciona Fecha y Hora</h2>
                    
                    <div class="mb-6">
                        <label class="block text-sm font-medium text-gray-700 mb-2">Fecha</label>
                        <input type="date" name="date" id="datePicker" min="{{ today }}" value="{{ today }}" 
                               class="block w-full px-4 py-3 rounded-lg border-gray-300 shadow-sm focus:ring-black focus:border-black"
                               onchange="fetchSlots()">
                    </div>

                    <div id="slotsContainer" class="grid grid-cols-3 md:grid-cols-5 gap-3">
                        <p class="text-sm text-gray-400 col-span-5">Selecciona un empleado para ver horarios.</p>
                    </div>
                </div>

                <div class="p-8 border-t border-gray-100 flex justify-between items-center bg-white">
                    <div>
                        <p class="text-xs text-gray-500 uppercase font-bold">Abono requerido</p>
                        <p class="text-2xl font-bold font-mono text-green-600">${{ deposit_amount|floatform:0 }}</p>
                    </div>
                    <button type="submit" id="submitBtn" disabled class="bg-gray-300 text-white px-8 py-4 rounded-xl font-bold shadow-none cursor-not-allowed transition-all">
                        Confirmar Reserva
                    </button>
                </div>
            </div>
        </form>

    </div>
</div>

<script>
    let currentEmployee = null;

    function selectEmployee(radio) {
        currentEmployee = radio.value;
        document.getElementById('selectedEmployee').value = currentEmployee;
        
        // Activar Paso 2
        const step2 = document.getElementById('step2');
        step2.classList.remove('opacity-50', 'pointer-events-none');
        
        // Cargar horarios
        fetchSlots();
    }

    function fetchSlots() {
        if (!currentEmployee) return;
        
        const date = document.getElementById('datePicker').value;
        const container = document.getElementById('slotsContainer');
        container.innerHTML = '<p class="text-sm text-gray-500 col-span-5 animate-pulse">Buscando disponibilidad...</p>';

        fetch(`{% url 'api_get_slots' %}?salon_id={{ salon.id }}&service_id={{ service.id }}&employee_id=${currentEmployee}&date=${date}`)
            .then(response => response.json())
            .then(data => {
                container.innerHTML = '';
                if (data.slots.length === 0) {
                    container.innerHTML = '<p class="text-sm text-red-500 col-span-5">No hay disponibilidad para esta fecha.</p>';
                    return;
                }

                data.slots.forEach(slot => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = `py-2 px-4 rounded-lg text-sm border-2 transition-all ${
                        slot.available 
                        ? 'bg-white border-gray-200 hover:border-black focus:bg-black focus:text-white' 
                        : 'bg-gray-100 border-transparent text-gray-400 cursor-not-allowed'
                    }`;
                    btn.innerText = slot.label;
                    btn.disabled = !slot.available;
                    
                    if (slot.available) {
                        btn.onclick = () => selectTime(slot.time, btn);
                    }
                    
                    container.appendChild(btn);
                });
            });
    }

    function selectTime(time, btnElement) {
        // Reset estilos botones
        const buttons = document.getElementById('slotsContainer').getElementsByTagName('button');
        for(let b of buttons) {
            if(!b.disabled) {
                b.classList.remove('bg-black', 'text-white', 'border-black');
                b.classList.add('bg-white', 'text-black', 'border-gray-200');
            }
        }
        
        // Activar seleccionado
        btnElement.classList.remove('bg-white', 'text-black', 'border-gray-200');
        btnElement.classList.add('bg-black', 'text-white', 'border-black');

        document.getElementById('selectedTime').value = time;
        
        // Habilitar botón final
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = false;
        submitBtn.classList.remove('bg-gray-300', 'shadow-none', 'cursor-not-allowed');
        submitBtn.classList.add('bg-black', 'shadow-lg', 'hover:scale-105');
    }
</script>
{% endblock %}
"""

# ==========================================
# 6. TEMPLATE CLIENT DASHBOARD (MIS CITAS)
# ==========================================
html_client_dash = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-serif font-bold mb-2">Mis Citas</h1>
    <p class="text-gray-500 mb-8">Gestiona tus reservas y pagos pendientes.</p>

    <div class="space-y-6">
        {% for app in appointments %}
        <div class="bg-white rounded-xl shadow border-l-4 {% if app.status == 'PENDING' %}border-yellow-400{% else %}border-green-500{% endif %} p-6 flex flex-col md:flex-row justify-between items-start md:items-center">
            
            <div class="mb-4 md:mb-0">
                <div class="flex items-center space-x-2 mb-1">
                    <h3 class="text-xl font-bold">{{ app.service.name }}</h3>
                    {% if app.status == 'PENDING' %}
                        <span class="bg-yellow-100 text-yellow-800 text-xs font-bold px-2 py-0.5 rounded">PENDIENTE PAGO</span>
                    {% else %}
                        <span class="bg-green-100 text-green-800 text-xs font-bold px-2 py-0.5 rounded">CONFIRMADA</span>
                    {% endif %}
                </div>
                <p class="text-gray-600">{{ app.salon.name }} &bull; con {{ app.employee.first_name }}</p>
                <p class="text-sm font-mono mt-1 text-gray-500">📅 {{ app.date_time|date:"D d M, Y - h:i A" }}</p>
            </div>

            <div class="w-full md:w-auto text-right">
                {% if app.status == 'PENDING' %}
                    <p class="text-xs text-red-500 font-bold mb-2">
                        Tiempo para pagar: <span id="timer-{{ app.id }}">--:--</span>
                    </p>
                    <a href="{{ app.wa_link }}" target="_blank" class="block w-full md:inline-block bg-green-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-green-700 transition shadow-lg flex items-center justify-center">
                        <span class="mr-2">📱</span> Enviar Abono (${{ app.deposit_amount|floatform:0 }})
                    </a>
                    
                    <script>
                        (function() {
                            let seconds = {{ app.seconds_left }};
                            const timerEl = document.getElementById('timer-{{ app.id }}');
                            
                            const interval = setInterval(() => {
                                if (seconds <= 0) {
                                    clearInterval(interval);
                                    timerEl.innerText = "EXPIRADO";
                                    return;
                                }
                                let m = Math.floor(seconds / 60);
                                let s = seconds % 60;
                                timerEl.innerText = `${m}:${s < 10 ? '0'+s : s}`;
                                seconds--;
                            }, 1000);
                        })();
                    </script>
                {% else %}
                    <button class="text-gray-400 text-sm border border-gray-200 px-4 py-2 rounded cursor-not-allowed">
                        Comprobante Enviado
                    </button>
                {% endif %}
            </div>

        </div>
        {% empty %}
        <div class="text-center py-12">
            <p class="text-gray-400">No tienes citas agendadas.</p>
            <a href="{% url 'marketplace_home' %}" class="mt-4 inline-block text-black underline font-bold">Ir al Marketplace</a>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 7. EJECUCIÓN
# ==========================================
def run_omega():
    print("🚀 INICIANDO FASE OMEGA (BOOKING COMPLETO)...")

    # 1. Marketplace Views
    with open(BASE_DIR / 'apps' / 'marketplace' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(marketplace_views.strip())
    print("✅ Marketplace Views: API y Guardado listos.")

    # 2. Marketplace URLs
    with open(BASE_DIR / 'apps' / 'marketplace' / 'urls.py', 'w', encoding='utf-8') as f:
        f.write(marketplace_urls.strip())
    print("✅ Marketplace URLs: Endpoints creados.")

    # 3. Core Views & URLs (Client Dash)
    update_core_views()
    update_core_urls()
    print("✅ Core: Dashboard de Cliente integrado.")

    # 4. Templates
    # Wizard
    with open(BASE_DIR / 'templates' / 'marketplace' / 'booking_wizard.html', 'w', encoding='utf-8') as f:
        f.write(html_wizard_js.strip())
    
    # Client Dash
    os.makedirs(BASE_DIR / 'templates' / 'core', exist_ok=True)
    with open(BASE_DIR / 'templates' / 'core' / 'client_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_client_dash.strip())
        
    print("✅ Templates: Wizard con JS y Dashboard Cliente creados.")

if __name__ == "__main__":
    run_omega()
    print("\n🦄 ¡LA PLATAFORMA ESTÁ COMPLETA!")
    print("Ahora un cliente puede registrarse, reservar una hora REAL y pagar por WhatsApp.")