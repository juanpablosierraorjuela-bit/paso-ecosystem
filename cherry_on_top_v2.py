import os
import subprocess
import urllib.parse # Para codificar el mensaje de WhatsApp

# -----------------------------------------------------------------------------
# 1. ACTUALIZAR SUCCESS.HTML (Diseño Hermoso + Política Clara + Cronómetro)
# -----------------------------------------------------------------------------
success_path = os.path.join('templates', 'booking', 'success.html')
print(f" Puliendo la joya en {success_path}...")

success_code = r"""{% extends 'base.html' %}
{% block content %}
<div class="container py-5 text-center">
    <div class="row justify-content-center">
        <div class="col-md-6">
            
            <div class="mb-4 animate-up">
                <div class="display-1 text-success mb-3"><i class="fas fa-check-circle"></i></div>
                <h1 class="fw-bold">¡Reserva Creada!</h1>
                <p class="lead text-muted">Tienes <span class="fw-bold text-danger bg-danger bg-opacity-10 px-2 rounded" id="timer">60:00</span> para realizar el abono.</p>
            </div>

            <div class="alert alert-warning border-0 rounded-4 mb-4 shadow-sm text-start animate-up" style="animation-delay: 0.1s;">
                <div class="d-flex">
                    <div class="me-3"><i class="fas fa-exclamation-triangle fs-4 text-warning"></i></div>
                    <div>
                        <h6 class="fw-bold mb-1">Política de Cancelación</h6>
                        <p class="mb-0 small opacity-75">
                             Si no asistes a la cita, <strong>pierdes el abono</strong>.<br>
                             Para reagendar sin penalidad, debes avisar con mínimo <strong>4 horas de anticipación</strong>.
                        </p>
                    </div>
                </div>
            </div>

            <div class="card border-0 shadow-sm rounded-4 bg-light mb-4 text-start animate-up" style="animation-delay: 0.2s;">
                <div class="card-body p-4">
                    <h5 class="fw-bold border-bottom pb-2 mb-3">Resumen de Pago</h5>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Total Servicio</span>
                        <span class="fw-bold">${{ booking.total_price|floatformat:0 }}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2 text-success">
                        <span>Abono Requerido ({{ booking.salon.deposit_percentage }}%)</span>
                        <span class="fw-bold fs-5">{{ deposit_fmt }}</span>
                    </div>
                    <small class="text-muted d-block mt-3 text-center bg-white p-2 rounded border border-dashed">
                        <i class="fas fa-info-circle me-1"></i> Paga el abono ahora. El restante lo pagas en el sitio.
                    </small>
                </div>
            </div>

            <a href="{{ whatsapp_url }}" target="_blank" class="btn btn-success btn-lg rounded-pill w-100 py-3 fw-bold shadow hover-scale mb-3 animate-up" style="animation-delay: 0.3s;">
                <i class="fab fa-whatsapp me-2 display-6 align-middle"></i> Enviar Comprobante y Confirmar
            </a>
            
            <p class="text-muted small mb-5">Al hacer clic, se abrirá WhatsApp con los datos de tu cita listos para enviar.</p>
            
            <a href="{% url 'marketplace' %}" class="btn btn-link text-muted text-decoration-none fw-bold">Volver al Inicio</a>
        </div>
    </div>
</div>

<script>
    // CRONÓMETRO AUTOMÁTICO DE 60 MINUTOS
    // Si el cliente no paga en este tiempo, sabe que su cita corre peligro.
    let duration = 60 * 60; // 60 minutos en segundos
    const display = document.querySelector('#timer');
    
    const timer = setInterval(function () {
        let minutes = parseInt(duration / 60, 10);
        let seconds = parseInt(duration % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--duration < 0) {
            clearInterval(timer);
            display.textContent = "TIEMPO AGOTADO";
            display.classList.remove('text-danger', 'bg-danger');
            display.classList.add('text-muted', 'bg-secondary');
            alert("El tiempo de reserva ha expirado. Por favor contacta al negocio.");
        }
    }, 1000);
</script>

<style>
    .hover-scale { transition: transform 0.2s; }
    .hover-scale:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(25, 135, 84, 0.3) !important; }
    
    .animate-up { opacity: 0; transform: translateY(20px); animation: fadeInUp 0.6s forwards; }
    @keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }
    
    .border-dashed { border-style: dashed !important; }
</style>
{% endblock %}
"""
with open(success_path, 'w', encoding='utf-8') as f:
    f.write(success_code)


# -----------------------------------------------------------------------------
# 2. ASEGURAR URLS.PY y VIEWS.PY (Por si no corriste el script anterior)
# -----------------------------------------------------------------------------
# Re-aplicamos la lógica de views y urls para garantizar que el sistema funcione completo.
views_path = os.path.join('apps', 'businesses', 'views.py')
print(f" Asegurando lógica en {views_path}...")

# (Nota: Usamos el mismo código de vista robusto del script anterior para no romper nada)
new_views_code = r"""from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SalonRegistrationForm, SalonSettingsForm, ServiceForm, EmployeeForm, EmployeeScheduleForm
from apps.core_saas.models import User
from .models import Salon, Service, Employee, Booking, EmployeeSchedule
from datetime import datetime, timedelta
import pytz
from django.utils import timezone
import urllib.parse 

# --- HELPERS ---
def get_available_slots(employee, date_obj, service):
    slots = []
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day_name = weekdays[date_obj.weekday()]
    schedule_str = getattr(employee.schedule, f"{day_name}_hours", "CERRADO")
    if schedule_str == "CERRADO": return []
    try:
        start_str, end_str = schedule_str.split('-')
        start_h, start_m = map(int, start_str.split(':'))
        end_h, end_m = map(int, end_str.split(':'))
        work_start = date_obj.replace(hour=start_h, minute=start_m, second=0)
        work_end = date_obj.replace(hour=end_h, minute=end_m, second=0)
        if work_end < work_start: work_end += timedelta(days=1)
        duration = timedelta(minutes=service.duration + service.buffer_time)
        current = work_start
        bogota_tz = pytz.timezone('America/Bogota')
        now_bogota = datetime.now(bogota_tz)
        while current + duration <= work_end:
            collision = Booking.objects.filter(employee=employee, status__in=['PENDING_PAYMENT', 'VERIFIED'], date_time__lt=current + duration, end_time__gt=current).exists()
            current_aware = pytz.timezone('America/Bogota').localize(current)
            is_future = current_aware > now_bogota
            if not collision and is_future: slots.append(current.strftime("%H:%M"))
            current += timedelta(minutes=30)
    except Exception as e: return []
    return slots

# --- FLOW DE RESERVAS ---
def booking_wizard_start(request):
    if request.method == 'POST':
        salon_id = request.POST.get('salon_id')
        service_id = request.POST.get('service_id')
        request.session['booking_salon'] = salon_id
        request.session['booking_service'] = service_id
        salon = get_object_or_404(Salon, id=salon_id)
        if not salon.employees.filter(is_active=True).exists():
            messages.error(request, f"Lo sentimos, {salon.name} no tiene profesionales disponibles.")
            return redirect('salon_detail', pk=salon_id)
        return redirect('booking_step_employee')
    return redirect('marketplace')

def booking_step_employee(request):
    salon_id = request.session.get('booking_salon')
    if not salon_id: return redirect('marketplace')
    salon = get_object_or_404(Salon, id=salon_id)
    return render(request, 'booking/step_employee.html', {'employees': salon.employees.filter(is_active=True)})

def booking_step_calendar(request):
    if request.method == 'POST': request.session['booking_employee'] = request.POST.get('employee_id')
    employee_id = request.session.get('booking_employee')
    service_id = request.session.get('booking_service')
    if not employee_id: return redirect('booking_step_employee')
    employee = get_object_or_404(Employee, id=employee_id)
    service = get_object_or_404(Service, id=service_id)
    today = datetime.now().date()
    selected_date_str = request.GET.get('date', str(today))
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    slots = get_available_slots(employee, datetime.combine(selected_date, datetime.min.time()), service)
    return render(request, 'booking/step_calendar.html', {'employee': employee, 'service': service, 'slots': slots, 'selected_date': selected_date_str, 'today': str(today)})

def booking_step_confirm(request):
    if request.method == 'POST': request.session['booking_time'] = request.POST.get('time')
    date_str = request.GET.get('date', datetime.now().strftime("%Y-%m-%d"))
    time_str = request.session.get('booking_time')
    service_id = request.session.get('booking_service')
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'booking/step_confirm.html', {'service': service, 'time': time_str, 'date': date_str})

def booking_create(request):
    if request.method == 'POST':
        salon_id = request.session.get('booking_salon')
        service_id = request.session.get('booking_service')
        employee_id = request.session.get('booking_employee')
        time_str = request.session.get('booking_time')
        date_str = request.POST.get('date_confirm') 
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        if not (salon_id and service_id and employee_id and time_str and date_str):
            messages.error(request, "Faltan datos de la reserva.")
            return redirect('marketplace')
        try:
            salon = get_object_or_404(Salon, id=salon_id)
            service = get_object_or_404(Service, id=service_id)
            employee = get_object_or_404(Employee, id=employee_id)
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            start_datetime = datetime.combine(date_obj, time_obj)
            total_price = service.price
            deposit_amount = total_price * (salon.deposit_percentage / 100)
            booking = Booking.objects.create(salon=salon, service=service, employee=employee, customer_name=customer_name, customer_phone=customer_phone, date_time=start_datetime, total_price=total_price, deposit_amount=deposit_amount, status='PENDING_PAYMENT')
            return redirect('booking_success', booking_id=booking.id)
        except Exception as e:
            messages.error(request, f"Error creando reserva: {e}")
            return redirect('marketplace')
    return redirect('marketplace')

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    salon = booking.salon
    remaining = booking.total_price - booking.deposit_amount
    total_fmt = "${:,.0f}".format(booking.total_price)
    deposit_fmt = "${:,.0f}".format(booking.deposit_amount)
    remaining_fmt = "${:,.0f}".format(remaining)
    message = (
        f"Hola *{salon.name}*, soy {booking.customer_name}.\n"
        f"Acabo de reservar una cita y quiero pagar el abono.\n\n"
        f" *Fecha:* {booking.date_time.strftime('%Y-%m-%d')}\n"
        f" *Hora:* {booking.date_time.strftime('%H:%M')}\n"
        f" *Servicio:* {booking.service.name}\n"
        f" *Profesional:* {booking.employee.name}\n\n"
        f" *Total Servicio:* {total_fmt}\n"
        f" *Abono a Pagar:* {deposit_fmt}\n"
        f" *Restante en sitio:* {remaining_fmt}\n\n"
        f"¿Qué medios de pago reciben para transferir el abono?"
    )
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{salon.whatsapp_number}?text={encoded_message}"
    return render(request, 'booking/success.html', {'booking': booking, 'whatsapp_url': whatsapp_url, 'deposit_fmt': deposit_fmt})

# --- OTRAS VISTAS (Dashboard, Auth, etc) ---
@login_required
def owner_dashboard(request):
    salon = request.user.salon
    pending_bookings = Booking.objects.filter(salon=salon, status='PENDING_PAYMENT').order_by('date_time')
    confirmed_bookings = Booking.objects.filter(salon=salon, status='VERIFIED').order_by('date_time')
    return render(request, 'dashboard/owner_dashboard.html', {'pending_bookings': pending_bookings, 'confirmed_bookings': confirmed_bookings})

@login_required
def verify_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, salon=request.user.salon)
    booking.status = 'VERIFIED'
    booking.save()
    messages.success(request, f"¡Cita de {booking.customer_name} confirmada!")
    return redirect('owner_dashboard')

# (Resto de vistas estándar para mantener funcionalidad completa)
@login_required
def employee_dashboard(request):
    employee = request.user.employee_profile
    bookings = Booking.objects.filter(employee=employee).order_by('date_time')
    return render(request, 'employee_dashboard.html', {'employee': employee, 'bookings': bookings})

@login_required
def employee_schedule(request):
    employee = request.user.employee_profile
    schedule, created = EmployeeSchedule.objects.get_or_create(employee=employee)
    if request.method == 'POST':
        form = EmployeeScheduleForm(request.POST, instance=schedule, salon=employee.salon)
        if form.is_valid(): form.save(); messages.success(request, "Horario actualizado."); return redirect('employee_schedule')
    else: form = EmployeeScheduleForm(instance=schedule, salon=employee.salon)
    return render(request, 'dashboard/employee_schedule.html', {'form': form, 'salon': employee.salon})

def saas_login(request):
    if request.method == 'POST':
        u = request.POST.get('username'); p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user: login(request, user); return redirect('owner_dashboard') if user.role == 'OWNER' else redirect('employee_dashboard')
        else: messages.error(request, "Credenciales inválidas")
    return render(request, 'registration/login.html')

def saas_logout(request): logout(request); return redirect('home')

def register_owner(request):
    if request.method == 'POST':
        form = SalonRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password1'], role='OWNER')
            Salon.objects.create(owner=user, name=form.cleaned_data['salon_name'], city=form.cleaned_data['city'], address=form.cleaned_data['address'], phone=form.cleaned_data['phone'], instagram_link=form.cleaned_data.get('instagram_link',''), maps_link=form.cleaned_data.get('maps_link',''))
            login(request, user); return redirect('owner_dashboard')
    else: form = SalonRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

def home(request): return render(request, 'home.html')

def marketplace(request):
    q = request.GET.get('q', ''); city = request.GET.get('city', '')
    salons = Salon.objects.all()
    if q: salons = salons.filter(name__icontains=q)
    if city: salons = salons.filter(city=city)
    return render(request, 'marketplace.html', {'salons': salons, 'cities': Salon.objects.values_list('city', flat=True).distinct()})

def salon_detail(request, pk): return render(request, 'salon_detail.html', {'salon': get_object_or_404(Salon, pk=pk)})
def landing_businesses(request): return render(request, 'landing_businesses.html')

@login_required
def owner_services(request): return render(request, 'dashboard/owner_services.html', {'services': request.user.salon.services.all()})
@login_required
def service_create(request):
    if request.method=='POST': 
        f=ServiceForm(request.POST); 
        if f.is_valid(): s=f.save(commit=False); s.salon=request.user.salon; s.save(); return redirect('owner_services')
    return render(request, 'dashboard/service_form.html', {'form': ServiceForm()})
@login_required
def service_update(request, pk):
    s=get_object_or_404(Service, pk=pk, salon=request.user.salon)
    if request.method=='POST': f=ServiceForm(request.POST, instance=s); f.save(); return redirect('owner_services') if f.is_valid() else None
    return render(request, 'dashboard/service_form.html', {'form': ServiceForm(instance=s)})
@login_required
def service_delete(request, pk):
    s=get_object_or_404(Service, pk=pk, salon=request.user.salon)
    if request.method=='POST': s.delete(); return redirect('owner_services')
    return render(request, 'dashboard/service_confirm_delete.html', {'object': s})

@login_required
def owner_employees(request): return render(request, 'dashboard/owner_employees.html', {'employees': request.user.salon.employees.all()})
@login_required
def employee_create(request):
    if request.method=='POST':
        f=EmployeeForm(request.POST)
        if f.is_valid():
            u=None; un=f.cleaned_data.get('username'); pw=f.cleaned_data.get('password')
            if un and pw: u=User.objects.create_user(username=un, password=pw, role='EMPLOYEE')
            e=f.save(commit=False); e.salon=request.user.salon; e.user=u; e.save(); EmployeeSchedule.objects.create(employee=e)
            return redirect('owner_employees')
    return render(request, 'dashboard/employee_form.html', {'form': EmployeeForm()})
@login_required
def employee_update(request, pk):
    e=get_object_or_404(Employee, pk=pk, salon=request.user.salon)
    if request.method=='POST': f=EmployeeForm(request.POST, instance=e); f.save(); return redirect('owner_employees') if f.is_valid() else None
    return render(request, 'dashboard/employee_form.html', {'form': EmployeeForm(instance=e)})
@login_required
def employee_delete(request, pk):
    e=get_object_or_404(Employee, pk=pk, salon=request.user.salon)
    if request.method=='POST': 
        if e.user: e.user.delete()
        e.delete(); return redirect('owner_employees')
    return render(request, 'dashboard/employee_confirm_delete.html', {'object': e})
@login_required
def owner_settings(request):
    s=request.user.salon
    if request.method=='POST': f=SalonSettingsForm(request.POST, instance=s); f.save(); messages.success(request, 'Guardado'); return redirect('owner_dashboard') if f.is_valid() else None
    return render(request, 'dashboard/owner_settings.html', {'form': SalonSettingsForm(instance=s)})
"""
with open(views_path, 'w', encoding='utf-8') as f:
    f.write(new_views_code)


# -----------------------------------------------------------------------------
# 3. SUBIR A GITHUB
# -----------------------------------------------------------------------------
print(" Subiendo mejoras finales a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Final Polish: Politica de Cancelacion + Cronometro 60min"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print(" ¡PERFECTO! La cereza del pastel ha sido colocada.")
except Exception as e:
    print(f" Error Git: {e}")

try:
    os.remove(__file__)
except:
    pass