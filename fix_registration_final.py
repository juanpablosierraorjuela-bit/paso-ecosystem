import os
import subprocess

# -----------------------------------------------------------------------------
# 1. CORREGIR FORMS.PY (Sacar passwords de Meta y mantener Dropdown)
# -----------------------------------------------------------------------------
forms_path = os.path.join("apps", "businesses", "forms.py")
print(f" Corrigiendo formulario en {forms_path}...")

new_forms_code = r"""from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee, EmployeeSchedule
from datetime import datetime

User = get_user_model()

# --- LISTA OFICIAL DE CIUDADES ---
COLOMBIA_CITIES = [
    ("Bogotá", "Bogotá"), ("Medellín", "Medellín"), ("Cali", "Cali"),
    ("Barranquilla", "Barranquilla"), ("Cartagena", "Cartagena"), ("Cúcuta", "Cúcuta"),
    ("Bucaramanga", "Bucaramanga"), ("Pereira", "Pereira"), ("Santa Marta", "Santa Marta"),
    ("Ibagué", "Ibagué"), ("Pasto", "Pasto"), ("Manizales", "Manizales"),
    ("Neiva", "Neiva"), ("Villavicencio", "Villavicencio"), ("Armenia", "Armenia"),
    ("Valledupar", "Valledupar"), ("Montería", "Montería"), ("Sincelejo", "Sincelejo"),
    ("Popayán", "Popayán"), ("Tunja", "Tunja"), ("Riohacha", "Riohacha"),
    ("Florencia", "Florencia"), ("Quibdó", "Quibdó"), ("Arauca", "Arauca"),
    ("Yopal", "Yopal"), ("Leticia", "Leticia"), ("San Andrés", "San Andrés"),
    ("Mocoa", "Mocoa"), ("Mitú", "Mitú"), ("Puerto Carreño", "Puerto Carreño"),
    ("Inírida", "Inírida"), ("San José del Guaviare", "San José del Guaviare"),
    ("Sogamoso", "Sogamoso"), ("Duitama", "Duitama"), ("Girardot", "Girardot"),
    ("Barrancabermeja", "Barrancabermeja"), ("Buenaventura", "Buenaventura"),
    ("Tumaco", "Tumaco"), ("Ipiales", "Ipiales"), ("Palmira", "Palmira"),
    ("Tuluá", "Tuluá"), ("Buga", "Buga"), ("Cartago", "Cartago"),
    ("Soacha", "Soacha"), ("Bello", "Bello"), ("Itagüí", "Itagüí"),
    ("Envigado", "Envigado"), ("Apartadó", "Apartadó"),
]

TIME_CHOICES = []
for h in range(5, 23):
    for m in (0, 30):
        time_str = f"{h:02d}:{m:02d}"
        display_str = datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
        TIME_CHOICES.append((time_str, display_str))

class EmployeeScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if self.instance.pk:
            for day in days:
                db_val = getattr(self.instance, f"{day}_hours", "CERRADO")
                is_active = db_val != "CERRADO"
                self.fields[f"{day}_active"].initial = is_active
                if is_active and "-" in db_val:
                    start, end = db_val.split("-")
                    self.fields[f"{day}_start"].initial = start
                    self.fields[f"{day}_end"].initial = end
        if self.salon:
            map_salon = {
                "monday": self.salon.work_monday, "tuesday": self.salon.work_tuesday,
                "wednesday": self.salon.work_wednesday, "thursday": self.salon.work_thursday,
                "friday": self.salon.work_friday, "saturday": self.salon.work_saturday,
                "sunday": self.salon.work_sunday
            }
            for day, works in map_salon.items():
                if not works:
                    self.fields[f"{day}_active"].disabled = True
                    self.fields[f"{day}_active"].initial = False

    monday_active = forms.BooleanField(required=False, label="Lunes")
    monday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    monday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    tuesday_active = forms.BooleanField(required=False, label="Martes")
    tuesday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    tuesday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    wednesday_active = forms.BooleanField(required=False, label="Miércoles")
    wednesday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    wednesday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    thursday_active = forms.BooleanField(required=False, label="Jueves")
    thursday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    thursday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    friday_active = forms.BooleanField(required=False, label="Viernes")
    friday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    friday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    saturday_active = forms.BooleanField(required=False, label="Sábado")
    saturday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    saturday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    sunday_active = forms.BooleanField(required=False, label="Domingo")
    sunday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    sunday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)

    class Meta:
        model = EmployeeSchedule
        fields = [] 

    def save(self, commit=True):
        schedule = super().save(commit=False)
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            is_active = self.cleaned_data.get(f"{day}_active")
            start = self.cleaned_data.get(f"{day}_start")
            end = self.cleaned_data.get(f"{day}_end")
            if is_active and start and end:
                setattr(schedule, f"{day}_hours", f"{start}-{end}")
            else:
                setattr(schedule, f"{day}_hours", "CERRADO")
        if commit: schedule.save()
        return schedule

class SalonRegistrationForm(forms.ModelForm):
    # Campos explícitos con widgets de Bootstrap
    username = forms.CharField(max_length=150, label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirmar Contraseña")
    
    salon_name = forms.CharField(max_length=255, label="Nombre del Negocio", widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Desplegable de ciudades
    city = forms.ChoiceField(
        choices=COLOMBIA_CITIES, 
        label="Ciudad", 
        initial="Bogotá",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    
    address = forms.CharField(max_length=255, label="Dirección", widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=50, label="WhatsApp / Teléfono", widget=forms.TextInput(attrs={'class': 'form-control'}))
    instagram_link = forms.URLField(required=False, label="Instagram", widget=forms.URLInput(attrs={'class': 'form-control'}))
    maps_link = forms.URLField(required=False, label="Google Maps", widget=forms.URLInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["username", "email"] # CORRECCIÓN: Quitamos passwords de aquí para evitar error de validación

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2: raise forms.ValidationError("Las contraseñas no coinciden")
        return p2

class SalonSettingsForm(forms.ModelForm):
    city = forms.ChoiceField(
        choices=COLOMBIA_CITIES, 
        label="Ciudad",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    class Meta:
        model = Salon
        fields = ["name", "city", "address", "whatsapp_number", "instagram_link", "maps_link", 
                  "opening_time", "closing_time", "deposit_percentage",
                  "work_monday", "work_tuesday", "work_wednesday", "work_thursday", "work_friday", "work_saturday", "work_sunday"]
        widgets = {
            "opening_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "closing_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "name": forms.TextInput(attrs={'class': 'form-control'}),
            "address": forms.TextInput(attrs={'class': 'form-control'}),
            "whatsapp_number": forms.TextInput(attrs={'class': 'form-control'}),
            "instagram_link": forms.URLInput(attrs={'class': 'form-control'}),
            "maps_link": forms.URLInput(attrs={'class': 'form-control'}),
            "deposit_percentage": forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "description", "duration", "price", "buffer_time", "is_active"]

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    class Meta:
        model = Employee
        fields = ["name", "phone", "instagram_link", "is_active"]
"""
with open(forms_path, "w", encoding="utf-8") as f:
    f.write(new_forms_code)


# -----------------------------------------------------------------------------
# 2. CORREGIR VIEWS.PY (Mapeo correcto de 'phone' a 'whatsapp_number')
# -----------------------------------------------------------------------------
views_path = os.path.join("apps", "businesses", "views.py")
print(f" Arreglando lógica de guardado en {views_path}...")

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

# --- VISTAS AUTH (Aquí estaba el error del registro) ---

def saas_login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            if user.role == 'OWNER': return redirect('owner_dashboard')
            return redirect('employee_dashboard')
        else:
            messages.error(request, "Credenciales inválidas")
    return render(request, 'registration/login.html')

def saas_logout(request):
    logout(request)
    return redirect('home')

def register_owner(request):
    if request.method == 'POST':
        form = SalonRegistrationForm(request.POST)
        if form.is_valid():
            # 1. Crear Usuario
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                role='OWNER'
            )
            
            # 2. Crear Salon (CORREGIDO: 'phone' del form va a 'whatsapp_number' del modelo)
            salon = Salon.objects.create(
                owner=user,
                name=form.cleaned_data['salon_name'],
                city=form.cleaned_data['city'],
                address=form.cleaned_data['address'],
                whatsapp_number=form.cleaned_data['phone'], # CORRECCIÓN CRÍTICA
                instagram_link=form.cleaned_data.get('instagram_link', ''),
                maps_link=form.cleaned_data.get('maps_link', '')
            )
            login(request, user)
            return redirect('owner_dashboard')
    else:
        form = SalonRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

# --- OTRAS VISTAS (Sin cambios importantes) ---
def home(request): return render(request, 'home.html')
def marketplace(request):
    q = request.GET.get('q', ''); city = request.GET.get('city', '')
    salons = Salon.objects.all()
    if q: salons = salons.filter(name__icontains=q)
    if city: salons = salons.filter(city=city)
    cities = Salon.objects.values_list('city', flat=True).distinct()
    return render(request, 'marketplace.html', {'salons': salons, 'cities': cities})
def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    return render(request, 'salon_detail.html', {'salon': salon})
def landing_businesses(request): return render(request, 'landing_businesses.html')

@login_required
def owner_services(request): return render(request, 'dashboard/owner_services.html', {'services': request.user.salon.services.all()})
@login_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            s = form.save(commit=False); s.salon = request.user.salon; s.save()
            return redirect('owner_services')
    else: form = ServiceForm()
    return render(request, 'dashboard/service_form.html', {'form': form})
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
with open(views_path, "w", encoding="utf-8") as f:
    f.write(new_views_code)

# -----------------------------------------------------------------------------
# 3. SUBIR A GITHUB
# -----------------------------------------------------------------------------
print(" Subiendo Arreglo Registro + WhatsApp a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix Critical: Correccion Registro (Phone -> Whatsapp) y Meta Fields"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print(" ¡LISTO! El registro ya debería funcionar sin errores.")
except Exception as e:
    print(f" Nota de Git: {e}")

try:
    os.remove(__file__)
except:
    pass