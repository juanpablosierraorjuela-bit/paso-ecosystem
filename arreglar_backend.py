import os

def get_models_content():
    return """from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
import pytz

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    description = models.TextField(verbose_name="Descripción", blank=True)
    city = models.CharField(max_length=100, verbose_name="Ciudad", default="Bogotá")
    address = models.CharField(max_length=255, verbose_name="Dirección Física")
    whatsapp_number = models.CharField(max_length=50, blank=True)
    instagram_link = models.URLField(blank=True)
    maps_link = models.URLField(blank=True)
    deposit_percentage = models.IntegerField(default=50)
    opening_time = models.TimeField(default="08:00")
    closing_time = models.TimeField(default="20:00")
    work_monday = models.BooleanField(default=True)
    work_tuesday = models.BooleanField(default=True)
    work_wednesday = models.BooleanField(default=True)
    work_thursday = models.BooleanField(default=True)
    work_friday = models.BooleanField(default=True)
    work_saturday = models.BooleanField(default=True)
    work_sunday = models.BooleanField(default=False)

    def __str__(self): return self.name

    @property
    def is_open_now(self):
        try:
            bogota = pytz.timezone('America/Bogota')
            now = datetime.now(bogota)
            current_time = now.time()
            today_idx = now.weekday()
            yesterday_idx = (today_idx - 1) % 7
            days_map = [self.work_monday, self.work_tuesday, self.work_wednesday, self.work_thursday, self.work_friday, self.work_saturday, self.work_sunday]
            
            # Turno HOY
            if days_map[today_idx]:
                if self.opening_time <= self.closing_time:
                    if self.opening_time <= current_time <= self.closing_time: return True
                else: # Nocturno
                    if current_time >= self.opening_time: return True
            
            # Turno AYER (Madrugada)
            if days_map[yesterday_idx] and self.opening_time > self.closing_time:
                if current_time <= self.closing_time: return True
        except Exception:
            return False
            
        return False

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(default=30)
    buffer_time = models.IntegerField(default=10)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Employee(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile', null=True, blank=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    instagram_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='schedule')
    monday_hours = models.CharField(max_length=50, default="09:00-18:00")
    tuesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    wednesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    thursday_hours = models.CharField(max_length=50, default="09:00-18:00")
    friday_hours = models.CharField(max_length=50, default="09:00-18:00")
    saturday_hours = models.CharField(max_length=50, default="09:00-18:00")
    sunday_hours = models.CharField(max_length=50, default="CERRADO")

class Booking(models.Model):
    STATUS_CHOICES = (('PENDING_PAYMENT', 'Pendiente'), ('VERIFIED', 'Confirmada'), ('COMPLETED', 'Completada'), ('CANCELLED', 'Cancelada'))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_PAYMENT')
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.end_time and self.service:
            total_min = self.service.duration + self.service.buffer_time
            self.end_time = self.date_time + timedelta(minutes=total_min)
        if not self.deposit_amount and self.salon:
            self.deposit_amount = self.total_price * (self.salon.deposit_percentage / 100)
        super().save(*args, **kwargs)
"""

def get_views_content():
    return """from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from apps.businesses.forms import SalonRegistrationForm
from apps.core_saas.models import User
from apps.businesses.models import Salon

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.method == 'POST':
        form = SalonRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                role='OWNER'
            )
            Salon.objects.create(
                owner=user,
                name=form.cleaned_data['salon_name'],
                city=form.cleaned_data['city'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                instagram_link=form.cleaned_data.get('instagram_link', ''),
                maps_link=form.cleaned_data.get('maps_link', '')
            )
            login(request, user)
            return redirect('owner_dashboard')
    else:
        form = SalonRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            if user.role == 'OWNER': return redirect('owner_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, 'registration/login.html')
"""

def write_file(path, content):
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Archivo reparado: {path}")

if __name__ == "__main__":
    print("🚑 INICIANDO REPARACIÓN DEL BACKEND...")
    
    # 1. Reparar Models (Agrega Employee que faltaba)
    write_file('apps/businesses/models.py', get_models_content())
    
    # 2. Reparar Core Views (Corrige importación de forms)
    # Detectamos si es 'core' o 'core_saas'
    if os.path.exists('apps/core_saas'):
        write_file('apps/core_saas/views.py', get_views_content())
    else:
        write_file('apps/core/views.py', get_views_content())

    print("\n✨ ¡Reparación completada! Ahora ejecuta:")
    print("1. git add .")
    print("2. git commit -m 'Fix: Repair backend models and views'")
    print("3. git push origin main")