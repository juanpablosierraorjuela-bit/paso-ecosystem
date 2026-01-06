from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SalonRegistrationForm, SalonSettingsForm, ServiceForm, EmployeeForm, EmployeeScheduleForm
from .models import Salon, Service, Employee, Booking, EmployeeSchedule
from datetime import datetime, timedelta
import pytz
from django.utils import timezone

# Fix de Importación Crítico
User = get_user_model()

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
        while current + duration <= work_end:
            collision = Booking.objects.filter(employee=employee, status__in=['PENDING_PAYMENT', 'VERIFIED'], date_time__lt=current + duration, end_time__gt=current).exists()
            bogota_tz = pytz.timezone('America/Bogota')
            now = datetime.now(bogota_tz)
            is_future = True
            if current.date() == now.date():
                current_aware = pytz.timezone('America/Bogota').localize(current)
                if current_aware < now: is_future = False
            if not collision and is_future: slots.append(current.strftime("%H:%M"))
            current += timedelta(minutes=30)
    except Exception as e:
        print(f"Error parsing slots: {e}")
        return []
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
            return redirect('businesses:salon_detail', pk=salon_id)
        return redirect('businesses:booking_step_employee')
    return redirect('businesses:marketplace')

def booking_step_employee(request):
    salon_id = request.session.get('booking_salon')
    if not salon_id: return redirect('businesses:marketplace')
    salon = get_object_or_404(Salon, id=salon_id)
    employees = salon.employees.filter(is_active=True)
    return render(request, 'booking/step_employee.html', {'employees': employees})

def booking_step_calendar(request):
    if request.method == 'POST': request.session['booking_employee'] = request.POST.get('employee_id')
    employee_id = request.session.get('booking_employee')
    service_id = request.session.get('booking_service')
    if not employee_id: return redirect('businesses:booking_step_employee')
    employee = get_object_or_404(Employee, id=employee_id)
    service = get_object_or_404(Service, id=service_id)
    today = datetime.now().date()
    selected_date_str = request.GET.get('date', str(today))
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    slots = get_available_slots(employee, datetime.combine(selected_date, datetime.min.time()), service)
    return render(request, 'booking/step_calendar.html', {'employee': employee, 'service': service, 'slots': slots, 'selected_date': selected_date_str, 'today': str(today)})

def booking_step_confirm(request):
    if request.method == 'POST': request.session['booking_time'] = request.POST.get('time')
    time_str = request.session.get('booking_time')
    date_str = request.GET.get('date', datetime.now().strftime("%Y-%m-%d"))
    service_id = request.session.get('booking_service')
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'booking/step_confirm.html', {'service': service, 'time': time_str, 'date': date_str})

def booking_create(request):
    if request.method == 'POST':
        return render(request, 'booking/success.html', {'wa_link': 'https://wa.me/'})
    return redirect('businesses:marketplace')

# --- VISTAS DASHBOARD ---
@login_required
def owner_dashboard(request):
    if not hasattr(request.user, 'salon'): return redirect('businesses:register_owner')
    pending_bookings = Booking.objects.filter(salon=request.user.salon, status='PENDING_PAYMENT')
    confirmed_bookings = Booking.objects.filter(salon=request.user.salon, status='VERIFIED')
    return render(request, 'dashboard/owner_dashboard.html', {'pending_bookings': pending_bookings, 'confirmed_bookings': confirmed_bookings})

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
        if form.is_valid():
            form.save()
            messages.success(request, "Horario actualizado con éxito.")
            return redirect('businesses:employee_schedule')
    else:
        form = EmployeeScheduleForm(instance=schedule, salon=employee.salon)
    return render(request, 'dashboard/employee_schedule.html', {'form': form, 'salon': employee.salon})

def register_owner(request):
    if request.method == 'POST':
        form = SalonRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password1'], role='OWNER')
            Salon.objects.create(owner=user, name=form.cleaned_data['salon_name'], city=form.cleaned_data['city'], address=form.cleaned_data['address'], phone=form.cleaned_data['phone'])
            login(request, user)
            return redirect('businesses:owner_dashboard')
    else:
        form = SalonRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

def home(request): return render(request, 'home.html')

def marketplace(request):
    salons = Salon.objects.all()
    return render(request, 'marketplace.html', {'salons': salons})

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    return render(request, 'salon_detail.html', {'salon': salon})

def landing_businesses(request): return render(request, 'landing_businesses.html')

@login_required
def owner_services(request):
    services = request.user.salon.services.all()
    return render(request, 'dashboard/owner_services.html', {'services': services})

@login_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            s = form.save(commit=False)
            s.salon = request.user.salon
            s.save()
            return redirect('businesses:owner_services')
    else:
        form = ServiceForm()
    return render(request, 'dashboard/service_form.html', {'form': form})

@login_required
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk, salon=request.user.salon)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid(): form.save(); return redirect('businesses:owner_services')
    else: form = ServiceForm(instance=service)
    return render(request, 'dashboard/service_form.html', {'form': form})

@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, salon=request.user.salon)
    if request.method == 'POST': service.delete(); return redirect('businesses:owner_services')
    return render(request, 'dashboard/service_confirm_delete.html', {'object': service})

@login_required
def owner_employees(request):
    employees = request.user.salon.employees.all()
    return render(request, 'dashboard/owner_employees.html', {'employees': employees})

@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user_emp = None
            if username and password:
                user_emp = User.objects.create_user(username=username, password=password, role='EMPLOYEE')
            emp = form.save(commit=False)
            emp.salon = request.user.salon
            emp.user = user_emp
            emp.save()
            EmployeeSchedule.objects.create(employee=emp)
            return redirect('businesses:owner_employees')
    else: form = EmployeeForm()
    return render(request, 'dashboard/employee_form.html', {'form': form})

@login_required
def employee_update(request, pk):
    emp = get_object_or_404(Employee, pk=pk, salon=request.user.salon)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=emp)
        if form.is_valid(): form.save(); return redirect('businesses:owner_employees')
    else: form = EmployeeForm(instance=emp)
    return render(request, 'dashboard/employee_form.html', {'form': form})

@login_required
def employee_delete(request, pk):
    emp = get_object_or_404(Employee, pk=pk, salon=request.user.salon)
    if request.method == 'POST':
        if emp.user: emp.user.delete()
        emp.delete()
        return redirect('businesses:owner_employees')
    return render(request, 'dashboard/employee_confirm_delete.html', {'object': emp})

@login_required
def verify_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, salon=request.user.salon)
    booking.status = 'VERIFIED'
    booking.save()
    messages.success(request, "Cita verificada correctamente.")
    return redirect('businesses:owner_dashboard')

@login_required
def owner_settings(request):
    salon = request.user.salon
    if request.method == 'POST':
        form = SalonSettingsForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración guardada.")
            return redirect('businesses:owner_dashboard')
    else: form = SalonSettingsForm(instance=salon)
    return render(request, 'dashboard/owner_settings.html', {'form': form})
