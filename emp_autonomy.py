import os
import subprocess

# -----------------------------------------------------------------------------
# 1. ACTUALIZAR VIEWS.PY (Separación de Paneles y Lógica de Horarios)
# -----------------------------------------------------------------------------
views_path = os.path.join("apps", "businesses", "views.py")
print(f" Configurando autonomía de empleados en {views_path}...")

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
        try:
            schedule = employee.schedule
        except ObjectDoesNotExist:
            return []

        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_name = weekdays[date_obj.weekday()]
        
        schedule_str = getattr(schedule, f"{day_name}_hours", "CERRADO")
        if schedule_str == "CERRADO": return []
            
        start_str, end_str = schedule_str.split("-")
        start_h, start_m = map(int, start_str.split(":"))
        end_h, end_m = map(int, end_str.split(":"))
        
        work_start = date_obj.replace(hour=start_h, minute=start_m, second=0)
        work_end = date_obj.replace(hour=end_h, minute=end_m, second=0)
        
        if work_end < work_start: work_end += timedelta(days=1)

        duration = timedelta(minutes=service.duration + service.buffer_time)
        current = work_start
        
        bogota_tz = pytz.timezone("America/Bogota")
        now_bogota = datetime.now(bogota_tz)

        while current + duration <= work_end:
            collision = Booking.objects.filter(
                employee=employee, 
                status__in=["PENDING_PAYMENT", "VERIFIED"], 
                date_time__lt=current + duration, 
                end_time__gt=current
            ).exists()
            
            current_aware = pytz.timezone("America/Bogota").localize(current)
            is_future = current_aware > now_bogota

            if not collision and is_future: 
                slots.append(current.strftime("%H:%M"))
            
            current += timedelta(minutes=30)
            
    except Exception as e:
        print(f"Error slots: {e}")
        return []
    return slots

# --- PANALES DIFERENCIADOS ---

@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER':
        return redirect('employee_dashboard')
    salon = request.user.salon
    pending = Booking.objects.filter(salon=salon, status='PENDING_PAYMENT').order_by('date_time')
    confirmed = Booking.objects.filter(salon=salon, status='VERIFIED').order_by('date_time')
    return render(request, 'dashboard/owner_dashboard.html', {'pending_bookings': pending, 'confirmed_bookings': confirmed})

@login_required
def employee_dashboard(request):
    try:
        employee = request.user.employee_profile
    except ObjectDoesNotExist:
        messages.error(request, "No tienes un perfil de empleado asignado.")
        return redirect('home')
        
    bookings = Booking.objects.filter(employee=employee).order_by('date_time')
    return render(request, 'employee_dashboard.html', {'employee': employee, 'bookings': bookings})

@login_required
def employee_schedule(request):
    try:
        employee = request.user.employee_profile
    except ObjectDoesNotExist:
        return redirect('home')
        
    schedule, created = EmployeeSchedule.objects.get_or_create(employee=employee)
    
    if request.method == "POST":
        form = EmployeeScheduleForm(request.POST, instance=schedule, salon=employee.salon)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu horario ha sido actualizado con éxito.")
            return redirect('employee_schedule')
    else:
        form = EmployeeScheduleForm(instance=schedule, salon=employee.salon)
    
    return render(request, 'dashboard/employee_schedule.html', {'form': form, 'salon': employee.salon})

# --- REGISTRO Y LOGIN ---

def register_owner(request):
    if request.method == "POST":
        form = SalonRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
                role="OWNER"
            )
            Salon.objects.create(
                owner=user,
                name=form.cleaned_data["salon_name"],
                city=form.cleaned_data["city"],
                address=form.cleaned_data["address"],
                whatsapp_number=form.cleaned_data["phone"]
            )
            login(request, user)
            return redirect("owner_dashboard")
    else:
        form = SalonRegistrationForm()
    return render(request, "registration/register_owner.html", {"form": form})

# (Mantenemos el resto de vistas: marketplace, booking_wizard, etc...)
def booking_wizard_start(request):
    if request.method == "POST":
        request.session["booking_salon"] = request.POST.get("salon_id")
        request.session["booking_service"] = request.POST.get("service_id")
        return redirect("booking_step_employee")
    return redirect("marketplace")

def booking_step_employee(request):
    salon_id = request.session.get("booking_salon")
    if not salon_id: return redirect("marketplace")
    salon = get_object_or_404(Salon, id=salon_id)
    return render(request, "booking/step_employee.html", {"employees": salon.employees.filter(is_active=True)})

def booking_step_calendar(request):
    employee_id = request.session.get("booking_employee")
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        request.session["booking_employee"] = employee_id
    
    service_id = request.session.get("booking_service")
    if not (employee_id and service_id): return redirect("marketplace")
    
    employee = get_object_or_404(Employee, id=employee_id)
    service = get_object_or_404(Service, id=service_id)
    today = datetime.now().date()
    selected_date_str = request.GET.get("date", str(today))
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except:
        selected_date = today

    slots = get_available_slots(employee, datetime.combine(selected_date, datetime.min.time()), service)
    return render(request, "booking/step_calendar.html", {"employee": employee, "service": service, "slots": slots, "selected_date": str(selected_date), "today": str(today)})

def booking_step_confirm(request):
    if request.method == "POST":
        request.session["booking_time"] = request.POST.get("time")
        request.session["booking_date"] = request.POST.get("date_selected")
    
    date_str = request.session.get("booking_date")
    time_str = request.session.get("booking_time")
    service_id = request.session.get("booking_service")
    if not (date_str and time_str and service_id): return redirect("booking_step_calendar")
    service = get_object_or_404(Service, id=service_id)
    return render(request, "booking/step_confirm.html", {"service": service, "time": time_str, "date": date_str})

def booking_create(request):
    if request.method == "POST":
        salon_id = request.session.get("booking_salon")
        service_id = request.session.get("booking_service")
        employee_id = request.session.get("booking_employee")
        time_str = request.session.get("booking_time")
        date_str = request.session.get("booking_date")
        if not (salon_id and service_id and employee_id and time_str and date_str): return redirect("marketplace")
        
        salon = get_object_or_404(Salon, id=salon_id)
        service = get_object_or_404(Service, id=service_id)
        employee = get_object_or_404(Employee, id=employee_id)
        start_dt = datetime.combine(datetime.strptime(date_str, "%Y-%m-%d").date(), datetime.strptime(time_str, "%H:%M").time())
        
        booking = Booking.objects.create(
            salon=salon, service=service, employee=employee,
            customer_name=request.POST.get("customer_name"),
            customer_phone=request.POST.get("customer_phone"),
            date_time=start_dt, total_price=service.price,
            deposit_amount=service.price * (salon.deposit_percentage/100),
            status="PENDING_PAYMENT"
        )
        return redirect("booking_success", booking_id=booking.id)
    return redirect("marketplace")

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    salon = booking.salon
    deposit_fmt = "${:,.0f}".format(booking.deposit_amount)
    msg = f"Hola *{salon.name}*, pago abono cita #{booking.id}\n {booking.date_time.strftime('%Y-%m-%d %H:%M')}\n Abono: {deposit_fmt}"
    whatsapp_url = f"https://wa.me/{salon.whatsapp_number}?text={urllib.parse.quote(msg)}"
    
    # Lógica de expiración (60 mins)
    elapsed = (timezone.now() - (booking.created_at if timezone.is_aware(booking.created_at) else timezone.make_aware(booking.created_at, pytz.timezone('America/Bogota')))).total_seconds()
    time_left = max(0, 3600 - elapsed)
    
    return render(request, "booking/success.html", {"booking": booking, "whatsapp_url": whatsapp_url, "deposit_fmt": deposit_fmt, "time_left_seconds": int(time_left), "is_expired": time_left <= 0})

def saas_login(request):
    if request.method == "POST":
        u = request.POST.get("username"); p = request.POST.get("password")
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return redirect("owner_dashboard") if user.role == "OWNER" else redirect("employee_dashboard")
        messages.error(request, "Credenciales inválidas")
    return render(request, "registration/login.html")

def saas_logout(request): logout(request); return redirect("home")
def home(request): return render(request, "home.html")
def marketplace(request):
    salons = Salon.objects.all()
    cities = Salon.objects.values_list("city", flat=True).distinct()
    return render(request, "marketplace.html", {"salons": salons, "cities": cities})
def salon_detail(request, pk): return render(request, "salon_detail.html", {"salon": get_object_or_404(Salon, pk=pk)})
def landing_businesses(request): return render(request, "landing_businesses.html")

@login_required
def owner_services(request): return render(request, "dashboard/owner_services.html", {"services": request.user.salon.services.all()})
@login_required
def service_create(request):
    if request.method == "POST":
        f = ServiceForm(request.POST); 
        if f.is_valid(): s = f.save(commit=False); s.salon = request.user.salon; s.save(); return redirect("owner_services")
    return render(request, "dashboard/service_form.html", {"form": ServiceForm()})
@login_required
def service_update(request, pk):
    s = get_object_or_404(Service, pk=pk, salon=request.user.salon)
    if request.method == "POST": f = ServiceForm(request.POST, instance=s); f.save(); return redirect("owner_services")
    return render(request, "dashboard/service_form.html", {"form": ServiceForm(instance=s)})
@login_required
def service_delete(request, pk):
    s = get_object_or_404(Service, pk=pk, salon=request.user.salon)
    if request.method == "POST": s.delete(); return redirect("owner_services")
    return render(request, "dashboard/service_confirm_delete.html", {"object": s})
@login_required
def owner_employees(request): return render(request, "dashboard/owner_employees.html", {"employees": request.user.salon.employees.all()})
@login_required
def employee_create(request):
    if request.method == "POST":
        f = EmployeeForm(request.POST)
        if f.is_valid():
            un = f.cleaned_data.get("username"); pw = f.cleaned_data.get("password")
            u = User.objects.create_user(username=un, password=pw, role="EMPLOYEE")
            e = f.save(commit=False); e.salon = request.user.salon; e.user = u; e.save()
            EmployeeSchedule.objects.create(employee=e)
            return redirect("owner_employees")
    return render(request, "dashboard/employee_form.html", {"form": EmployeeForm()})
@login_required
def employee_update(request, pk):
    e = get_object_or_404(Employee, pk=pk, salon=request.user.salon)
    if request.method == "POST": f = EmployeeForm(request.POST, instance=e); f.save(); return redirect("owner_employees")
    return render(request, "dashboard/employee_form.html", {"form": EmployeeForm(instance=e)})
@login_required
def employee_delete(request, pk):
    e = get_object_or_404(Employee, pk=pk, salon=request.user.salon)
    if request.method == "POST": 
        if e.user: e.user.delete()
        e.delete(); return redirect("owner_employees")
    return render(request, "dashboard/employee_confirm_delete.html", {"object": e})
@login_required
def verify_booking(request, pk):
    b = get_object_or_404(Booking, pk=pk, salon=request.user.salon); b.status = "VERIFIED"; b.save(); return redirect("owner_dashboard")
@login_required
def owner_settings(request):
    s = request.user.salon
    if request.method == "POST": f = SalonSettingsForm(request.POST, instance=s); f.save(); return redirect("owner_dashboard")
    return render(request, "dashboard/owner_settings.html", {"form": SalonSettingsForm(instance=s)})
"""

with open(views_path, "w", encoding="utf-8") as f:
    f.write(new_views_code)

# -----------------------------------------------------------------------------
# 2. ACTUALIZAR TEMPLATE DE HORARIOS (Interfaz Pro con Selectores)
# -----------------------------------------------------------------------------
schedule_path = os.path.join("templates", "dashboard", "employee_schedule.html")
print(f" Creando interfaz de horarios inteligente en {schedule_path}...")

new_schedule_html = r"""{% extends 'master.html' %}
{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-10">
            <div class="card border-0 shadow-lg rounded-4">
                <div class="card-header bg-dark text-white p-4">
                    <h3 class="mb-0 fw-bold"><i class="fas fa-clock me-2"></i> Mi Horario de Trabajo</h3>
                    <p class="text-white-50 mb-0">Define los días y horas en los que estás disponible para los clientes.</p>
                </div>
                <div class="card-body p-4 p-md-5">
                    <form method="post" class="needs-validation">
                        {% csrf_token %}
                        
                        <div class="table-responsive">
                            <table class="table table-hover align-middle">
                                <thead class="table-light">
                                    <tr>
                                        <th>Día</th>
                                        <th>¿Trabajas?</th>
                                        <th>Hora Inicio</th>
                                        <th>Hora Fin</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for day_code, day_name in form.day_fields %}
                                    <tr class="{% if not day_name.is_salon_open %}table-secondary{% endif %}">
                                        <td class="fw-bold text-dark">{{ day_name.label }}</td>
                                        <td>
                                            <div class="form-check form-switch">
                                                {{ day_name.active_field }}
                                            </div>
                                        </td>
                                        <td>{{ day_name.start_field }}</td>
                                        <td>{{ day_name.end_field }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>

                        <div class="d-grid mt-4">
                            <button type="submit" class="btn btn-dark btn-lg rounded-pill shadow-sm py-3 fw-bold">
                                <i class="fas fa-save me-2"></i> GUARDAR MI DISPONIBILIDAD
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    .form-switch .form-check-input { width: 3em; height: 1.5em; cursor: pointer; }
    .form-select { border-radius: 10px; border: 1px solid #dee2e6; padding: 0.5rem; }
    .form-select:disabled { background-color: #f8f9fa; color: #adb5bd; }
</style>

<script>
    // Lógica para deshabilitar selectores si el switch está apagado
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        const row = checkbox.closest('tr');
        const selects = row.querySelectorAll('select');
        
        const updateState = () => {
            selects.forEach(s => s.disabled = !checkbox.checked);
        };
        
        checkbox.addEventListener('change', updateState);
        updateState(); // Inicial
    });
</script>
{% endblock %}
"""
with open(schedule_path, "w", encoding="utf-8") as f:
    f.write(new_schedule_html)

# -----------------------------------------------------------------------------
# 3. ACTUALIZAR FORMS.PY (Lógica de los Selectores de Horas)
# -----------------------------------------------------------------------------
forms_path = os.path.join("apps", "businesses", "forms.py")
print(f" Actualizando lógica de formularios en {forms_path}...")

new_forms_code = r"""from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee, EmployeeSchedule
from datetime import datetime

User = get_user_model()

COLOMBIA_CITIES = [("Bogotá", "Bogotá"), ("Medellín", "Medellín"), ("Cali", "Cali"), ("Tunja", "Tunja")]
TIME_CHOICES = [(f"{h:02d}:{m:02d}", datetime.strptime(f"{h:02d}:{m:02d}", "%H:%M").strftime("%I:%M %p")) for h in range(5, 23) for m in (0, 30)]

class EmployeeScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        self.day_fields = []
        days = [('monday', 'Lunes'), ('tuesday', 'Martes'), ('wednesday', 'Miércoles'), ('thursday', 'Jueves'), ('friday', 'Viernes'), ('saturday', 'Sábado'), ('sunday', 'Domingo')]
        
        for code, label in days:
            active_name = f"{code}_active"
            start_name = f"{code}_start"
            end_name = f"{code}_end"
            
            # Campos Dinámicos
            self.fields[active_name] = forms.BooleanField(required=False, label=label, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
            self.fields[start_name] = forms.ChoiceField(choices=TIME_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
            self.fields[end_name] = forms.ChoiceField(choices=TIME_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
            
            # Cargar datos iniciales
            db_val = getattr(self.instance, f"{code}_hours", "CERRADO")
            if db_val != "CERRADO" and '-' in db_val:
                s, e = db_val.split('-')
                self.fields[active_name].initial = True
                self.fields[start_name].initial = s
                self.fields[end_name].initial = e
            
            # Bloquear si el salón cierra ese día
            salon_open = getattr(self.salon, f"work_{code}", True)
            if not salon_open:
                self.fields[active_name].widget.attrs['disabled'] = True
                self.fields[active_name].initial = False

            self.day_fields.append((code, {
                'label': label,
                'active_field': self[active_name],
                'start_field': self[start_name],
                'end_field': self[end_name],
                'is_salon_open': salon_open
            }))

    class Meta:
        model = EmployeeSchedule
        fields = []

    def save(self, commit=True):
        instance = super().save(commit=False)
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            if self.cleaned_data.get(f"{day}_active"):
                setattr(instance, f"{day}_hours", f"{self.cleaned_data[day+'_start']}-{self.cleaned_data[day+'_end']}")
            else:
                setattr(instance, f"{day}_hours", "CERRADO")
        if commit: instance.save()
        return instance

class SalonRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    salon_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username', 'email']
    def clean_password2(self):
        if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'): raise forms.ValidationError("No coinciden")
        return self.cleaned_data.get('password2')

class SalonSettingsForm(forms.ModelForm):
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, widget=forms.Select(attrs={'class': 'form-select'}))
    class Meta:
        model = Salon
        fields = ['name', 'city', 'address', 'whatsapp_number', 'opening_time', 'closing_time', 'deposit_percentage', 'work_monday', 'work_tuesday', 'work_wednesday', 'work_thursday', 'work_friday', 'work_saturday', 'work_sunday']
        widgets = {'opening_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), 'closing_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})}

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'buffer_time', 'is_active']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'}), 'duration': forms.NumberInput(attrs={'class': 'form-control'}), 'price': forms.NumberInput(attrs={'class': 'form-control'})}

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    class Meta:
        model = Employee
        fields = ['name', 'phone', 'instagram_link', 'is_active']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}
"""
with open(forms_path, "w", encoding="utf-8") as f:
    f.write(new_forms_code)

# -----------------------------------------------------------------------------
# 4. SUBIR CAMBIOS
# -----------------------------------------------------------------------------
print(" Subiendo autonomía de empleados a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Feat: Panel de empleado autonomo con selectores de hora y jerarquia de salon"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print(" ¡SISTEMA ACTUALIZADO! El empleado ahora es dueño de su tiempo.")
except Exception as e:
    print(f" Error Git: {e}")

try:
    os.remove(__file__)
except:
    pass