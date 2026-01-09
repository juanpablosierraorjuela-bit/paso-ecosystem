import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. MARKETPLACE VIEWS (LOGICA DE AUTO-REGISTRO)
# ==========================================
marketplace_views = """
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
from apps.businesses.models import Salon, Service
from apps.core.models import User
from apps.businesses.logic import AvailabilityManager
from apps.marketplace.models import Appointment
import uuid

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

# --- WIZARD VISUAL (ABIERTO A TODOS) ---
def booking_wizard(request, salon_id, service_id):
    # NOTA: Ya no requiere login previo
    salon = get_object_or_404(Salon, pk=salon_id)
    service = get_object_or_404(Service, pk=service_id, salon=salon)
    employees = salon.employees.all()
    
    deposit_amount = (service.price * salon.deposit_percentage) / 100
    
    context = {
        'salon': salon,
        'service': service,
        'employees': employees,
        'deposit_amount': deposit_amount,
        'today': timezone.localtime(timezone.now()).strftime('%Y-%m-%d'),
        'is_guest': not request.user.is_authenticated # Flag para mostrar form de datos
    }
    return render(request, 'marketplace/booking_wizard.html', context)

# --- API: OBTENER HORAS (ABIERTO) ---
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

# --- CONFIRMAR RESERVA (AUTO-REGISTRO) ---
def booking_commit(request):
    if request.method == 'POST':
        salon_id = request.POST.get('salon_id')
        service_id = request.POST.get('service_id')
        employee_id = request.POST.get('employee_id')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        
        # Datos del Cliente (Si es guest)
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

        # --- LÓGICA DE USUARIO ---
        client_user = request.user

        if not client_user.is_authenticated:
            # 1. Verificar si ya existe
            if User.objects.filter(email=email).exists():
                messages.error(request, "Este correo ya está registrado. Por favor inicia sesión primero.")
                return redirect('login') # O idealmente volver al wizard con error
            
            # 2. Crear Usuario Automáticamente
            # Generamos contraseña temporal aleatoria
            temp_password = str(uuid.uuid4())[:8]
            
            client_user = User.objects.create_user(
                username=email, # Usamos email como username
                email=email,
                password=temp_password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='CLIENT',
                is_verified_payment=True # Clientes no pagan suscripción mensual
            )
            
            # 3. Auto-Login
            login(request, client_user)
            messages.success(request, f"¡Cuenta creada! Tu contraseña temporal es: {temp_password} (Cámbiala en perfil)")

        # --- CREAR CITA ---
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
# 2. TEMPLATE WIZARD (CON CAMPOS DE DATOS)
# ==========================================
html_wizard = """
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

                <div class="p-8 border-b border-gray-100 bg-gray-50 transition-opacity duration-300 opacity-50 pointer-events-none" id="step2">
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

                {% if is_guest %}
                <div class="p-8 border-b border-gray-100 bg-white transition-opacity duration-300 opacity-50 pointer-events-none" id="step3">
                    <h2 class="text-lg font-bold mb-4">3. Tus Datos (Registro Automático)</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-gray-500 mb-1">Nombre</label>
                            <input type="text" name="first_name" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-black focus:border-black">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 mb-1">Apellido</label>
                            <input type="text" name="last_name" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-black focus:border-black">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 mb-1">WhatsApp</label>
                            <input type="text" name="phone" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-black focus:border-black">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 mb-1">Correo Electrónico</label>
                            <input type="email" name="email" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-black focus:border-black">
                        </div>
                    </div>
                </div>
                {% endif %}

                <div class="p-8 border-t border-gray-100 flex justify-between items-center bg-gray-50">
                    <div>
                        <p class="text-xs text-gray-500 uppercase font-bold">Abono requerido</p>
                        <p class="text-2xl font-bold font-mono text-green-600">${{ deposit_amount|floatform:0 }}</p>
                    </div>
                    <button type="submit" id="submitBtn" disabled class="bg-gray-300 text-white px-8 py-4 rounded-xl font-bold shadow-none cursor-not-allowed transition-all">
                        Pagar Abono y Confirmar
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
        step2.classList.add('bg-white');
        
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
        // Reset estilos
        const buttons = document.getElementById('slotsContainer').getElementsByTagName('button');
        for(let b of buttons) {
            if(!b.disabled) {
                b.classList.remove('bg-black', 'text-white', 'border-black');
                b.classList.add('bg-white', 'text-black', 'border-gray-200');
            }
        }
        
        // Activar
        btnElement.classList.remove('bg-white', 'text-black', 'border-gray-200');
        btnElement.classList.add('bg-black', 'text-white', 'border-black');

        document.getElementById('selectedTime').value = time;
        
        // Activar Paso 3 (si existe) o Botón Submit
        const step3 = document.getElementById('step3');
        const submitBtn = document.getElementById('submitBtn');
        
        if (step3) {
            step3.classList.remove('opacity-50', 'pointer-events-none');
            // Hacer scroll suave hacia abajo
            step3.scrollIntoView({behavior: "smooth"});
        }
        
        // Habilitar botón
        submitBtn.disabled = false;
        submitBtn.classList.remove('bg-gray-300', 'shadow-none', 'cursor-not-allowed');
        submitBtn.classList.add('bg-black', 'shadow-lg', 'hover:scale-105');
    }
</script>
{% endblock %}
"""

# ==========================================
# 3. EJECUTAR (APLICAR LOS CAMBIOS)
# ==========================================
def run_fix():
    print("🚀 ACTIVANDO MODO 'FRICTIONLESS BOOKING'...")

    # 1. Views
    with open(BASE_DIR / 'apps' / 'marketplace' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(marketplace_views.strip())
    print("✅ apps/marketplace/views.py: Auto-registro activado.")

    # 2. Template
    with open(BASE_DIR / 'templates' / 'marketplace' / 'booking_wizard.html', 'w', encoding='utf-8') as f:
        f.write(html_wizard.strip())
    print("✅ templates/marketplace/booking_wizard.html: Formulario de datos integrado.")

if __name__ == "__main__":
    run_fix()
    print("\n🦄 LISTO. Ahora los clientes pueden reservar sin registrarse antes.")