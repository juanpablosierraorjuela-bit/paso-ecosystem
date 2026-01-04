import os
import subprocess
import urllib.parse

# -----------------------------------------------------------------------------
# 1. ACTUALIZAR VIEWS.PY (Lógica de Fecha Blindada + Cronómetro Real)
# -----------------------------------------------------------------------------
views_path = os.path.join('apps', 'businesses', 'views.py')
print(f" Reparando el motor de reservas en {views_path}...")

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
    # Recibir empleado
    if request.method == 'POST': 
        request.session['booking_employee'] = request.POST.get('employee_id')
    
    employee_id = request.session.get('booking_employee')
    service_id = request.session.get('booking_service')
    if not employee_id: return redirect('booking_step_employee')
    
    employee = get_object_or_404(Employee, id=employee_id)
    service = get_object_or_404(Service, id=service_id)
    
    # Manejo de fecha (GET para navegación, Default Hoy)
    today = datetime.now().date()
    selected_date_str = request.GET.get('date', str(today))
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
        selected_date = today
        selected_date_str = str(today)

    slots = get_available_slots(employee, datetime.combine(selected_date, datetime.min.time()), service)
    
    return render(request, 'booking/step_calendar.html', {
        'employee': employee, 'service': service, 'slots': slots, 
        'selected_date': selected_date_str, 'today': str(today)
    })

def booking_step_confirm(request):
    # Recibir hora y fecha del formulario anterior
    if request.method == 'POST': 
        request.session['booking_time'] = request.POST.get('time')
        # IMPORTANTE: Guardamos la fecha en sesión también para no perderla
        request.session['booking_date'] = request.POST.get('date_selected')
    
    date_str = request.session.get('booking_date')
    time_str = request.session.get('booking_time')
    service_id = request.session.get('booking_service')

    # Validación de seguridad
    if not (date_str and time_str and service_id):
        messages.error(request, "Por favor selecciona una fecha y hora válidas.")
        return redirect('booking_step_calendar')

    service = get_object_or_404(Service, id=service_id)
    return render(request, 'booking/step_confirm.html', {'service': service, 'time': time_str, 'date': date_str})

def booking_create(request):
    if request.method == 'POST':
        salon_id = request.session.get('booking_salon')
        service_id = request.session.get('booking_service')
        employee_id = request.session.get('booking_employee')
        time_str = request.session.get('booking_time')
        
        # Recuperamos fecha del input hidden O de la sesión (doble seguridad)
        date_str = request.POST.get('date_confirm') or request.session.get('booking_date')
        
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        
        if not (salon_id and service_id and employee_id and time_str and date_str):
            messages.error(request, "Faltan datos de la reserva. Intenta nuevamente.")
            return redirect('marketplace')
        try:
            salon = get_object_or_404(Salon, id=salon_id)
            service = get_object_or_404(Service, id=service_id)
            employee = get_object_or_404(Employee, id=employee_id)
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            start_datetime = datetime.combine(date_obj, time_obj)
            
            # Verificar duplicados al momento de crear (Seguridad extra)
            if Booking.objects.filter(employee=employee, date_time=start_datetime, status__in=['PENDING_PAYMENT', 'VERIFIED']).exists():
                messages.error(request, "Lo sentimos, alguien acaba de tomar ese horario.")
                return redirect('booking_step_calendar')

            total_price = service.price
            deposit_amount = total_price * (salon.deposit_percentage / 100)
            
            booking = Booking.objects.create(
                salon=salon, service=service, employee=employee, 
                customer_name=customer_name, customer_phone=customer_phone, 
                date_time=start_datetime, total_price=total_price, 
                deposit_amount=deposit_amount, status='PENDING_PAYMENT'
            )
            return redirect('booking_success', booking_id=booking.id)
        except Exception as e:
            messages.error(request, f"Error técnico: {e}")
            return redirect('marketplace')
    return redirect('marketplace')

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    salon = booking.salon
    
    # --- LÓGICA DE CRONÓMETRO REAL ---
    # Calculamos cuánto tiempo ha pasado desde la creación
    # Usamos timezone.now() si created_at tiene zona horaria
    created_at = booking.created_at
    if timezone.is_naive(created_at):
        created_at = timezone.make_aware(created_at, pytz.timezone('America/Bogota'))
        
    now = timezone.now()
    elapsed = (now - created_at).total_seconds()
    time_left_seconds = max(0, 3600 - elapsed) # 3600 segundos = 60 minutos
    
    is_expired = time_left_seconds <= 0

    remaining = booking.total_price - booking.deposit_amount
    total_fmt = "${:,.0f}".format(booking.total_price)
    deposit_fmt = "${:,.0f}".format(booking.deposit_amount)
    remaining_fmt = "${:,.0f}".format(remaining)
    
    message = (
        f"Hola *{salon.name}*, soy {booking.customer_name}.\n"
        f"Pago Abono Cita #{booking.id}\n"
        f" {booking.date_time.strftime('%Y-%m-%d %H:%M')}\n"
        f" {booking.service.name}\n"
        f" Abono: {deposit_fmt}\n"
        f"¿Me regalas datos para transferir?"
    )
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{salon.whatsapp_number}?text={encoded_message}"
    
    return render(request, 'booking/success.html', {
        'booking': booking, 'whatsapp_url': whatsapp_url, 'deposit_fmt': deposit_fmt,
        'time_left_seconds': int(time_left_seconds), 'is_expired': is_expired
    })

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

# (Resto de vistas estándar)
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
# 2. ACTUALIZAR STEP_CALENDAR.HTML (Para que envíe la FECHA por POST)
# -----------------------------------------------------------------------------
calendar_path = os.path.join('templates', 'booking', 'step_calendar.html')
print(f" Corrigiendo el calendario en {calendar_path}...")

calendar_code = r"""{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
                <div class="card-header bg-white p-4 text-center border-bottom">
                    <h4 class="fw-bold mb-1">Selecciona tu Hora</h4>
                    <p class="text-muted mb-0">{{ service.name }} con <span class="fw-bold text-dark">{{ employee.name }}</span></p>
                </div>
                
                <div class="card-body p-4">
                    <div class="d-flex justify-content-center align-items-center gap-3 mb-4">
                        <button class="btn btn-light rounded-circle shadow-sm" onclick="changeDate(-1)"><i class="fas fa-chevron-left"></i></button>
                        <h5 class="mb-0 fw-bold">{{ selected_date }}</h5>
                        <button class="btn btn-light rounded-circle shadow-sm" onclick="changeDate(1)"><i class="fas fa-chevron-right"></i></button>
                    </div>

                    {% if slots %}
                        <form action="{% url 'booking_step_confirm' %}" method="post">
                            {% csrf_token %}
                            <input type="hidden" name="date_selected" value="{{ selected_date }}">
                            
                            <div class="row g-3">
                                {% for slot in slots %}
                                <div class="col-4 col-sm-3 col-md-2">
                                    <input type="radio" class="btn-check" name="time" id="slot_{{ forloop.counter }}" value="{{ slot }}" required>
                                    <label class="btn btn-outline-dark w-100 rounded-3 py-2" for="slot_{{ forloop.counter }}">
                                        {{ slot }}
                                    </label>
                                </div>
                                {% endfor %}
                            </div>

                            <div class="d-grid mt-5">
                                <button type="submit" class="btn btn-dark btn-lg rounded-pill fw-bold shadow-sm">
                                    Continuar <i class="fas fa-arrow-right ms-2"></i>
                                </button>
                            </div>
                        </form>
                    {% else %}
                        <div class="text-center py-5">
                            <div class="text-muted mb-3"><i class="far fa-calendar-times fa-3x"></i></div>
                            <h5>No hay cupos para esta fecha.</h5>
                            <p class="text-muted small">Intenta buscar en otro día.</p>
                        </div>
                    {% endif %}
                </div>
            </div>
            <div class="text-center mt-3">
                <a href="{% url 'booking_step_employee' %}" class="text-muted text-decoration-none small">Cambiar Profesional</a>
            </div>
        </div>
    </div>
</div>

<script>
    function changeDate(days) {
        const current = new Date("{{ selected_date }}");
        current.setDate(current.getDate() + days);
        // Formato YYYY-MM-DD simple
        const nextDate = current.toISOString().split('T')[0];
        window.location.href = "?date=" + nextDate;
    }
</script>
{% endblock %}
"""
with open(calendar_path, 'w', encoding='utf-8') as f:
    f.write(calendar_code)


# -----------------------------------------------------------------------------
# 3. ACTUALIZAR SUCCESS.HTML (Panel de Cliente Persistente + Cronómetro Pro)
# -----------------------------------------------------------------------------
success_path = os.path.join('templates', 'booking', 'success.html')
print(f" Creando el Panel de Cliente en {success_path}...")

success_code = r"""{% extends 'base.html' %}
{% block content %}
<div class="container py-5 text-center">
    <div class="row justify-content-center">
        <div class="col-md-7">
            
            {% if is_expired %}
                <div class="card border-0 shadow-lg rounded-4 p-5 text-center bg-light">
                    <div class="text-danger display-1 mb-3"><i class="far fa-times-circle"></i></div>
                    <h2 class="fw-bold text-danger">Reserva Cancelada</h2>
                    <p class="text-muted">El tiempo para realizar el abono ha expirado.</p>
                    <a href="{% url 'marketplace' %}" class="btn btn-dark rounded-pill mt-3 px-4">Nueva Reserva</a>
                </div>
            {% else %}
                <div class="mb-4 animate-up">
                    <div class="display-1 text-success mb-3"><i class="fas fa-check-circle"></i></div>
                    <h1 class="fw-bold">¡Cita Pendiente de Abono!</h1>
                    <p class="lead text-muted">Tu cita está reservada temporalmente.</p>
                </div>

                <div class="card border-0 shadow-sm rounded-4 bg-danger bg-opacity-10 mb-4 animate-up text-center py-3">
                    <p class="mb-0 text-danger fw-bold small text-uppercase">Tiempo restante para verificar</p>
                    <div class="display-4 fw-bold text-danger" id="timer">Calculating...</div>
                </div>

                <div class="alert alert-light border shadow-sm rounded-4 mb-4 text-start animate-up">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-shield-alt fs-3 text-warning me-3"></i>
                        <div>
                            <h6 class="fw-bold mb-1">Política de Cancelación y Abonos</h6>
                            <p class="mb-0 small text-muted">
                                Si no asistes, el abono no es reembolsable. Cancelaciones con menos de 4 horas de anticipación pierden el abono.
                            </p>
                        </div>
                    </div>
                </div>

                <div class="card border-0 shadow-lg rounded-4 overflow-hidden mb-4 text-start animate-up">
                    <div class="card-header bg-white p-4 border-bottom">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="fw-bold mb-0">Resumen de Cita #{{ booking.id }}</h5>
                            <span class="badge bg-warning text-dark">Pendiente</span>
                        </div>
                    </div>
                    <div class="card-body p-4">
                        <div class="row g-3">
                            <div class="col-6">
                                <small class="text-muted d-block">Servicio</small>
                                <strong>{{ booking.service.name }}</strong>
                            </div>
                            <div class="col-6 text-end">
                                <small class="text-muted d-block">Profesional</small>
                                <strong>{{ booking.employee.name }}</strong>
                            </div>
                            <div class="col-6">
                                <small class="text-muted d-block">Fecha</small>
                                <strong>{{ booking.date_time|date:"D d M, Y" }}</strong>
                            </div>
                            <div class="col-6 text-end">
                                <small class="text-muted d-block">Hora</small>
                                <strong>{{ booking.date_time|date:"h:i A" }}</strong>
                            </div>
                        </div>
                        <hr class="my-4">
                        <div class="d-flex justify-content-between mb-2">
                            <span>Valor Total</span>
                            <span class="fw-bold">${{ booking.total_price|floatformat:0 }}</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center p-3 bg-success bg-opacity-10 rounded-3">
                            <span class="text-success fw-bold">Abono a Pagar Ahora</span>
                            <span class="fs-4 fw-bold text-success">{{ deposit_fmt }}</span>
                        </div>
                    </div>
                </div>

                <a href="{{ whatsapp_url }}" target="_blank" class="btn btn-success btn-lg rounded-pill w-100 py-3 fw-bold shadow hover-scale mb-3 animate-up">
                    <i class="fab fa-whatsapp me-2 display-6 align-middle"></i> Pagar Abono en WhatsApp
                </a>
                <p class="text-muted small mb-5">Envía el comprobante para que el negocio verifique tu cita.</p>
            {% endif %}

        </div>
    </div>
</div>

<script>
    {% if not is_expired %}
    // Cronómetro Real Persistente
    let timeLeft = {{ time_left_seconds }};
    const display = document.querySelector('#timer');
    
    function updateTimer() {
        let minutes = parseInt(timeLeft / 60, 10);
        let seconds = parseInt(timeLeft % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (timeLeft <= 0) {
            location.reload(); // Recargar para mostrar estado caducado
        } else {
            timeLeft--;
        }
    }
    
    // Iniciar
    updateTimer();
    setInterval(updateTimer, 1000);
    {% endif %}
</script>

<style>
    .hover-scale { transition: transform 0.2s; }
    .hover-scale:hover { transform: translateY(-3px); }
    .animate-up { opacity: 0; transform: translateY(20px); animation: fadeInUp 0.6s forwards; }
    @keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }
</style>
{% endblock %}
"""
with open(success_path, 'w', encoding='utf-8') as f:
    f.write(success_code)


# -----------------------------------------------------------------------------
# 4. SUBIR A GITHUB
# -----------------------------------------------------------------------------
print(" Subiendo solución definitiva a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix Critical: Reparar flujo de Fecha + Panel Cliente + Cronometro Real"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print(" ¡HECHO! El sistema ahora es robusto y hermoso.")
except Exception as e:
    print(f" Error Git: {e}")

try:
    os.remove(__file__)
except:
    pass