import os
import sys

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
VIEWS_PATH = os.path.join(APP_DIR, "views.py")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
CLIENT_DASH_PATH = os.path.join(TEMPLATES_DIR, "client_dashboard.html")
OWNER_DASH_PATH = os.path.join(TEMPLATES_DIR, "dashboard", "owner_dashboard.html")

# --- 1. VIEWS.PY RECARGADO (CEREBRO DE RESERVAS) ---
CONTENIDO_VIEWS = """from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, date, time
from .models import Salon, Service, Employee, SalonSchedule, EmployeeSchedule, Booking
from .forms import OwnerRegistrationForm, SalonForm, ServiceForm, EmployeeForm, EmployeeCreationForm

User = get_user_model()

# --- PÚBLICO ---
def home(request): return render(request, 'home.html')
def marketplace(request): return render(request, 'marketplace.html', {'salons': Salon.objects.all()})
def salon_detail(request, salon_id): return render(request, 'salon_detail.html', {'salon': get_object_or_404(Salon, id=salon_id)})
def landing_businesses(request): return render(request, 'landing_businesses.html')

# --- WIZARD DE RESERVAS (LA JOYA DE LA CORONA) ---
@login_required
def booking_wizard(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    step = request.GET.get('step', '1')
    
    # Paso 1: Seleccionar Servicios
    if step == '1':
        if request.method == 'POST':
            request.session['booking_services'] = request.POST.getlist('services')
            return redirect(f'/reservar/{salon.id}/?step=2')
        return render(request, 'booking/step_services.html', {'salon': salon, 'services': salon.services.all()})

    # Paso 2: Seleccionar Empleado
    elif step == '2':
        if request.method == 'POST':
            request.session['booking_employee'] = request.POST.get('employee')
            return redirect(f'/reservar/{salon.id}/?step=3')
        return render(request, 'booking/step_employee.html', {'salon': salon, 'employees': salon.employees.all()})

    # Paso 3: Fecha y Hora (CORREGIDO TIMEZONE)
    elif step == '3':
        if request.method == 'POST':
            date_str = request.POST.get('date')
            time_str = request.POST.get('time')
            # Guardamos en sesión como string para evitar errores de serialización
            request.session['booking_date'] = date_str
            request.session['booking_time'] = time_str
            return redirect(f'/reservar/{salon.id}/?step=4')
        return render(request, 'booking/step_calendar.html', {'salon': salon})

    # Paso 4: Confirmación y Creación
    elif step == '4':
        service_ids = request.session.get('booking_services', [])
        employee_id = request.session.get('booking_employee')
        date_str = request.session.get('booking_date')
        time_str = request.session.get('booking_time')

        services = Service.objects.filter(id__in=service_ids)
        employee = get_object_or_404(Employee, id=employee_id)
        total_price = sum(s.price for s in services)
        deposit = total_price * 0.5 # 50% de abono

        if request.method == 'POST':
            # AQUI SE CREA LA CITA (ESTADO PENDING/AMARILLO)
            booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            booking_time = datetime.strptime(time_str, "%H:%M").time()
            
            # MAGIA TIMEZONE: Combinamos y hacemos "aware"
            naive_datetime = datetime.combine(booking_date, booking_time)
            aware_datetime = timezone.make_aware(naive_datetime) # ESTO SOLUCIONA EL BUCLE

            booking = Booking.objects.create(
                customer=request.user,
                salon=salon,
                employee=employee,
                date=booking_date,
                time=booking_time,
                total_price=total_price,
                deposit_amount=deposit,
                status='pending' # Nace en Amarillo
            )
            booking.services.set(services)
            
            # Limpiar sesión
            del request.session['booking_services']
            del request.session['booking_employee']
            
            return redirect('client_dashboard')

        return render(request, 'booking/step_confirm.html', {
            'salon': salon,
            'services': services,
            'employee': employee,
            'date': date_str,
            'time': time_str,
            'total': total_price,
            'deposit': deposit
        })
    
    return redirect('home')

# --- DASHBOARD CLIENTE (SEMÁFORO) ---
@login_required
def client_dashboard(request):
    bookings = Booking.objects.filter(customer=request.user).order_by('-date')
    return render(request, 'client_dashboard.html', {'bookings': bookings})

# --- REDIRECCIÓN INTELIGENTE ---
@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'salon'): return redirect('owner_dashboard')
    elif hasattr(request.user, 'employee_profile'): return redirect('employee_dashboard')
    else: return redirect('client_dashboard')

# --- REGISTRO Y LOGIN ---
class RegisterOwnerView(CreateView):
    template_name = 'registration/register_owner.html'
    form_class = OwnerRegistrationForm
    success_url = '/dashboard/'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_form'] = OwnerRegistrationForm()
        ctx['salon_form'] = SalonForm()
        return ctx
    def post(self, request, *args, **kwargs):
        user_form = OwnerRegistrationForm(request.POST)
        salon_form = SalonForm(request.POST)
        if user_form.is_valid() and salon_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            salon = salon_form.save(commit=False)
            salon.owner = user
            salon.save()
            SalonSchedule.objects.create(salon=salon)
            login(request, user)
            return redirect('owner_dashboard')
        return render(request, self.template_name, {'user_form': user_form, 'salon_form': salon_form})

# --- VISTAS DEL DUEÑO (CRUD) ---
@method_decorator(login_required, name='dispatch')
class OwnerDashboardView(TemplateView):
    template_name = 'dashboard/owner_dashboard.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try: ctx['salon'] = self.request.user.salon
        except: ctx['salon'] = None
        # Agregamos las citas pendientes para que el dueño las vea
        if ctx['salon']:
            ctx['pending_bookings'] = Booking.objects.filter(salon=ctx['salon'], status='pending')
        return ctx

# (Para simplificar, mantenemos las otras vistas de servicios y empleados existentes)
# --- REINCORPORANDO VISTAS DE SERVICIOS Y EMPLEADOS ---
@method_decorator(login_required, name='dispatch')
class OwnerServicesView(ListView):
    model = Service
    template_name = 'dashboard/owner_services.html'
    context_object_name = 'services'
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')
    def form_valid(self, form):
        form.instance.salon = self.request.user.salon
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'dashboard/service_confirm_delete.html'
    success_url = reverse_lazy('owner_services')
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class OwnerEmployeesView(ListView):
    model = Employee
    template_name = 'dashboard/owner_employees.html'
    context_object_name = 'employees'
    def get_queryset(self): return Employee.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeCreationForm
    template_name = 'dashboard/employee_form.html'
    success_url = reverse_lazy('owner_employees')
    def form_valid(self, form):
        user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'])
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        employee = form.save(commit=False)
        employee.salon = self.request.user.salon
        employee.user = user
        employee.save()
        EmployeeSchedule.objects.create(employee=employee)
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class OwnerSettingsView(UpdateView):
    model = SalonSchedule
    template_name = 'dashboard/owner_settings.html'
    fields = ['monday_open', 'tuesday_open', 'wednesday_open', 'thursday_open', 'friday_open', 'saturday_open', 'sunday_open']
    success_url = reverse_lazy('owner_settings')
    def get_object(self, queryset=None):
        schedule, created = SalonSchedule.objects.get_or_create(salon=self.request.user.salon)
        return schedule
    
@login_required
def employee_dashboard(request):
    return render(request, 'employee_dashboard.html', {'employee': request.user.employee_profile})
"""

# --- 2. DASHBOARD CLIENTE (SEMÁFORO Y WHATSAPP) ---
CONTENIDO_CLIENT_DASH = """{% extends 'base.html' %}
{% load humanize %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold">Mis Reservas</h2>
        <a href="{% url 'marketplace' %}" class="btn btn-dark">Nueva Reserva</a>
    </div>

    <div class="row">
        {% for booking in bookings %}
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-body p-4">
                    <div class="d-flex justify-content-between mb-3">
                        <h5 class="fw-bold text-dark">{{ booking.salon.name }}</h5>
                        {% if booking.status == 'pending' %}
                            <span class="badge bg-warning text-dark px-3 py-2 rounded-pill">
                                <i class="bi bi-hourglass-split"></i> Pendiente de Pago
                            </span>
                        {% elif booking.status == 'confirmed' %}
                            <span class="badge bg-success px-3 py-2 rounded-pill">
                                <i class="bi bi-check-circle-fill"></i> Verificada
                            </span>
                        {% else %}
                            <span class="badge bg-secondary">Cancelada</span>
                        {% endif %}
                    </div>
                    
                    <p class="mb-1 text-muted"><i class="bi bi-calendar-event"></i> {{ booking.date }} a las {{ booking.time }}</p>
                    <p class="mb-1 text-muted"><i class="bi bi-person"></i> {{ booking.employee.first_name }}</p>
                    <p class="mb-3 text-muted"><i class="bi bi-scissors"></i> 
                        {% for s in booking.services.all %}{{ s.name }}{% if not forloop.last %}, {% endif %}{% endfor %}
                    </p>
                    
                    <div class="d-flex justify-content-between align-items-center bg-light p-3 rounded mb-3">
                        <div>
                            <small class="text-muted d-block">Total</small>
                            <span class="fw-bold">${{ booking.total_price|intcomma }}</span>
                        </div>
                        <div>
                            <small class="text-muted d-block">Abono (50%)</small>
                            <span class="fw-bold text-dark">${{ booking.deposit_amount|intcomma }}</span>
                        </div>
                    </div>

                    {% if booking.status == 'pending' %}
                    <div class="d-grid">
                        <a href="https://wa.me/{{ booking.salon.whatsapp }}?text=Hola {{ booking.salon.name }}, quiero confirmar mi reserva del {{ booking.date }} a las {{ booking.time }}. Mi nombre es {{ user.first_name }}. ¿A qué cuenta consigno el abono de ${{ booking.deposit_amount }}?" 
                           target="_blank" 
                           class="btn btn-warning fw-bold text-dark">
                            <i class="bi bi-whatsapp"></i> Pagar Abono
                        </a>
                        <small class="text-center text-muted mt-2">Envía el comprobante para verificar tu cita.</small>
                    </div>
                    {% endif %}
                    
                    {% if booking.status == 'confirmed' %}
                    <div class="alert alert-success mb-0 text-center small">
                        <i class="bi bi-shield-check"></i> ¡Tu cupo está blindado!
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-12 text-center py-5">
            <h3 class="text-muted">Aún no tienes citas.</h3>
            <p>Explora el marketplace y agenda tu primer servicio.</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

def actualizar_archivos():
    print("🧠 Actualizando Views.py (Wizard corregido y Timezone)...")
    with open(VIEWS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_VIEWS)

    print("🚦 Actualizando Client Dashboard (Semáforo y WhatsApp)...")
    with open(CLIENT_DASH_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_CLIENT_DASH)

if __name__ == "__main__":
    print("🚀 INICIANDO ACTUALIZACIÓN MASTER 🚀")
    actualizar_archivos()
    print("\n✅ Archivos actualizados. Ejecuta los comandos de git para subir.")