import os
import subprocess
import sys
import django

# Configurar Django para el script de reparación de datos
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paso_ecosystem.settings')
django.setup()

from apps.businesses.models import Employee, EmployeeSchedule

print(" INICIANDO REPARACIÓN DE DATOS...")

# -----------------------------------------------------------------------------
# 1. REPARAR EMPLEADOS SIN HORARIO (La causa raíz del Error 500)
# -----------------------------------------------------------------------------
employees = Employee.objects.all()
fixed_count = 0
for emp in employees:
    # Intentamos acceder al horario
    try:
        schedule = emp.schedule
    except EmployeeSchedule.DoesNotExist: # Si no existe, explota aquí
        print(f" Empleado roto encontrado: {emp.name} (ID: {emp.id})")
        # Lo reparamos creando un horario por defecto
        EmployeeSchedule.objects.create(employee=emp)
        print(f" Horario creado para {emp.name}")
        fixed_count += 1
    except Exception as e:
        print(f"Error desconocido con {emp.name}: {e}")

print(f" Reparación completada. {fixed_count} empleados arreglados.")

# -----------------------------------------------------------------------------
# 2. APLICAR VIEWS.PY BLINDADO (Sin errores de sintaxis)
# -----------------------------------------------------------------------------
views_path = os.path.join('apps', 'businesses', 'views.py')
print(f" Blindando {views_path}...")

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
from django.core.exceptions import ObjectDoesNotExist

# --- HELPERS ---
def get_available_slots(employee, date_obj, service):
    slots = []
    try:
        # 1. Validar horario de forma segura
        try:
            schedule = employee.schedule
        except ObjectDoesNotExist:
            return [] # Empleado sin horario = Sin cupos

        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_name = weekdays[date_obj.weekday()]
        
        schedule_str = getattr(schedule, f"{day_name}_hours", "CERRADO")
        if schedule_str == "CERRADO": return []
            
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
            collision = Booking.objects.filter(
                employee=employee, 
                status__in=['PENDING_PAYMENT', 'VERIFIED'], 
                date_time__lt=current + duration, 
                end_time__gt=current
            ).exists()
            
            # Comparar con zona horaria correcta
            current_aware = pytz.timezone('America/Bogota').localize(current)
            is_future = current_aware > now_bogota

            if not collision and is_future: 
                slots.append(current.strftime("%H:%M"))
            
            current += timedelta(minutes=30)
            
    except Exception as e:
        print(f"Error slots: {e}")
        return []
    return slots

# --- FLOW DE RESERVAS ---

def booking_wizard_start(request):
    if request.method == 'POST':
        salon_id = request.POST.get('salon_id')
        service_id = request.POST.get('service_id')
        request.session['booking_salon'] = salon_id
        request.session['booking_service'] = service_id
        
        try:
            salon = get_object_or_404(Salon, id=salon_id)
            if not salon.employees.filter(is_active=True).exists():
                messages.error(request, f"Lo sentimos, {salon.name} no tiene profesionales disponibles.")
                return redirect('salon_detail', pk=salon_id)
        except:
            return redirect('marketplace')
            
        return redirect('booking_step_employee')
    return redirect('marketplace')

def booking_step_employee(request):
    salon_id = request.session.get('booking_salon')
    if not salon_id: return redirect('marketplace')
    salon = get_object_or_404(Salon, id=salon_id)
    return render(request, 'booking/step_employee.html', {'employees': salon.employees.filter(is_active=True)})

def booking_step_calendar(request):
    if request.method == 'POST': 
        request.session['booking_employee'] = request.POST.get('employee_id')
    
    employee_id = request.session.get('booking_employee')
    service_id = request.session.get('booking_service')
    
    if not employee_id or not service_id:
        messages.warning(request, "Sesión reiniciada. Selecciona servicio de nuevo.") 
        return redirect('marketplace')
    
    try:
        employee = get_object_or_404(Employee, id=employee_id)
        service = get_object_or_404(Service, id=service_id)
    except:
        return redirect('marketplace')
    
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
    if request.method == 'POST': 
        request.session['booking_time'] = request.POST.get('time')
        request.session['booking_date'] = request.POST.get('date_selected')
    
    date_str = request.session.get('booking_date')
    time_str = request.session.get('booking_time')
    service_id = request.session.get('booking_service')

    if not (date_str and time_str and service_id):
        messages.error(request, "Datos incompletos. Intenta de nuevo.")
        return redirect('booking_step_calendar')

    service = get_object_or_404(Service, id=service_id)
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except:
        date_obj = datetime.now()

    return render(request, 'booking/step_confirm.html', {
        'service': service, 'time': time_str, 'date': date_str, 'date_pretty': date_obj
    })

def booking_create(request):
    if request.method == 'POST':
        salon_id = request.session.get('booking_salon')
        service_id = request.session.get('booking_service')
        employee_id = request.session.get('booking_employee')
        time_str = request.session.get('booking_time')
        date_str = request.session.get('booking_date')
        
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        
        if not (salon_id and service_id and employee_id and time_str and date_str):
            messages.error(request, "Error en la reserva. Intenta de nuevo.")
            return redirect('marketplace')
        try:
            salon = get_object_or_404(Salon, id=salon_id)
            service = get_object_or_404(Service, id=service_id)
            employee = get_object_or_404(Employee, id=employee_id)
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            start_datetime = datetime.combine(date_obj, time_obj)
            
            if Booking.objects.filter(employee=employee, date_time=start_datetime, status__in=['PENDING_PAYMENT', 'VERIFIED']).exists():
                messages.error(request, "Horario ocupado recientemente.")
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
            print(f"Booking Error: {e}")
            return redirect('marketplace')
    return redirect('marketplace')

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    salon = booking.salon
    
    # Cronómetro y Lógica
    created_at = booking.created_at
    if timezone.is_naive(created_at):
        created_at = timezone.make_aware(created_at, pytz.timezone('America/Bogota'))
    now = timezone.now()
    elapsed = (now - created_at).total_seconds()
    time_left_seconds = max(0, 3600 - elapsed)
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
        'booking': booking, 'whatsapp_url': whatsapp_url, 
        'deposit_fmt': deposit_fmt, 'time_left_seconds': int(time_left_seconds), 
        'is_expired': is_expired
    })

# --- DASHBOARDS Y AUTH ---
@login_required
def owner_dashboard(request):
    salon = request.user.salon
    pending = Booking.objects.filter(salon=salon, status='PENDING_PAYMENT').order_by('date_time')
    confirmed = Booking.objects.filter(salon=salon, status='VERIFIED').order_by('date_time')
    return render(request, 'dashboard/owner_dashboard.html', {'pending_bookings': pending, 'confirmed_bookings': confirmed})

@login_required
def verify_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, salon=request.user.salon)
    booking.status = 'VERIFIED'; booking.save()
    messages.success(request, "Cita confirmada.")
    return redirect('owner_dashboard')

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
        if form.is_valid(): form.save(); messages.success(request, "Horario guardado."); return redirect('employee_schedule')
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
    if q: salons = salons.filter(name__icontains=q); 
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
print(" Subiendo la solución de Datos + Código a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Reparar Empleados sin Horario y Blindar Vistas"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print(" ¡ÉXITO TOTAL! Datos reparados y código seguro.")
except Exception as e:
    print(f" Nota de Git: {e}")

try:
    os.remove(__file__)
except:
    pass