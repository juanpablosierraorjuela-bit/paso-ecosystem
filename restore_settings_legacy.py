import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
TEMPLATES_DASH_DIR = os.path.join(BASE_DIR, "templates", "dashboard")

VIEWS_PATH = os.path.join(APP_DIR, "views.py")
SETTINGS_HTML_PATH = os.path.join(TEMPLATES_DASH_DIR, "owner_settings.html")

# --- 1. VIEWS.PY (LÓGICA BLINDADA + RESCATE DE DATOS) ---
CONTENIDO_VIEWS = """from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, date, time
from django.contrib import messages

from .models import Salon, Service, Employee, SalonSchedule, EmployeeSchedule, Booking
from .forms import (
    OwnerRegistrationForm, SalonForm, ServiceForm, 
    EmployeeForm, EmployeeCreationForm, SalonScheduleForm
)

User = get_user_model()

# ... (Vistas generales mantenidas) ...
def home(request): return render(request, 'home.html')
def marketplace(request): return render(request, 'marketplace.html', {'salons': Salon.objects.all()})
def salon_detail(request, salon_id): return render(request, 'salon_detail.html', {'salon': get_object_or_404(Salon, id=salon_id)})
def landing_businesses(request): return render(request, 'landing_businesses.html')

@login_required
def booking_wizard(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    return render(request, 'booking/step_calendar.html', {'salon': salon})

@login_required
def client_dashboard(request):
    bookings = Booking.objects.filter(customer=request.user).order_by('-date')
    return render(request, 'client_dashboard.html', {'bookings': bookings})

@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'salon'): return redirect('owner_dashboard')
    elif hasattr(request.user, 'employee_profile'): return redirect('employee_dashboard')
    else: return redirect('client_dashboard')

# --- REGISTRO (CON LA LÓGICA DE WHATSAPP AUTOMÁTICO) ---
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
            # Lógica rescatada: Si ponen teléfono, se asume WhatsApp
            salon.whatsapp = salon_form.cleaned_data['phone']
            salon.save()
            SalonSchedule.objects.create(salon=salon)
            login(request, user)
            return redirect('owner_dashboard')
        return render(request, self.template_name, {'user_form': user_form, 'salon_form': salon_form})

# --- DASHBOARD ---
@method_decorator(login_required, name='dispatch')
class OwnerDashboardView(TemplateView):
    template_name = 'dashboard/owner_dashboard.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try: ctx['salon'] = self.request.user.salon
        except: ctx['salon'] = None
        if ctx['salon']:
            ctx['pending_bookings'] = Booking.objects.filter(salon=ctx['salon'], status='pending')
        return ctx

# --- CONFIGURACIÓN (LÓGICA MEJORADA) ---
@login_required
def owner_settings_view(request):
    try:
        salon = request.user.salon
    except Salon.DoesNotExist:
        return redirect('home')

    schedule, created = SalonSchedule.objects.get_or_create(salon=salon)

    if request.method == 'POST':
        salon_form = SalonForm(request.POST, instance=salon)
        schedule_form = SalonScheduleForm(request.POST, instance=schedule)

        if salon_form.is_valid() and schedule_form.is_valid():
            salon_obj = salon_form.save(commit=False)
            # Aseguramos que el WhatsApp se actualice si cambian el teléfono
            if salon_obj.phone:
                salon_obj.whatsapp = salon_obj.phone
            salon_obj.save()
            schedule_form.save()
            messages.success(request, '¡Tu negocio se ha actualizado correctamente!')
            return redirect('owner_settings')
        else:
            messages.error(request, 'Hubo un error. Revisa los campos en rojo.')
    else:
        salon_form = SalonForm(instance=salon)
        schedule_form = SalonScheduleForm(instance=schedule)

    return render(request, 'dashboard/owner_settings.html', {
        'salon_form': salon_form,
        'schedule_form': schedule_form
    })

class OwnerSettingsView(TemplateView):
    def as_view(self=None, **initkwargs):
        return owner_settings_view

# --- VISTAS CRUD DE SERVICIOS Y EMPLEADOS ---
@method_decorator(login_required, name='dispatch')
class OwnerServicesView(ListView):
    model = Service
    template_name = 'dashboard/owner_services.html'
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
    success_url = reverse_lazy('owner_services')
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class OwnerEmployeesView(ListView):
    model = Employee
    template_name = 'dashboard/owner_employees.html'
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

@login_required
def employee_dashboard(request):
    return render(request, 'employee_dashboard.html', {'employee': request.user.employee_profile})
"""

# --- 2. HTML RESTAURADO (ESTILO DEL BACKUP + FUNCIONALIDAD NUEVA) ---
CONTENIDO_HTML = """{% extends 'master.html' %}
{% load static %}

{% block content %}
<div class="container py-5">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h2 class="fw-bold text-dark">Configuración del Negocio</h2>
            <p class="text-muted mb-0">Administra tu identidad y disponibilidad en el marketplace.</p>
        </div>
        <a href="{% url 'owner_dashboard' %}" class="btn btn-outline-secondary rounded-pill">
            <i class="bi bi-arrow-left"></i> Volver al Panel
        </a>
    </div>

    <form method="post" class="row g-4">
        {% csrf_token %}

        {% if messages %}
        <div class="col-12">
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show shadow-sm" role="alert">
                    <i class="bi bi-check-circle-fill me-2"></i> {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        </div>
        {% endif %}

        <div class="col-lg-5">
            <div class="card shadow-lg border-0 rounded-4 overflow-hidden h-100">
                <div class="card-header bg-dark text-white py-3">
                    <h5 class="mb-0 fw-bold"><i class="bi bi-shop-window me-2"></i> Identidad</h5>
                </div>
                <div class="card-body p-4">
                    <div class="mb-3">
                        <label class="form-label fw-bold small text-secondary">NOMBRE DEL NEGOCIO</label>
                        {{ salon_form.name }}
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-6">
                            <label class="form-label fw-bold small text-secondary">CIUDAD</label>
                            {{ salon_form.city }}
                        </div>
                        <div class="col-6">
                            <label class="form-label fw-bold small text-secondary">CELULAR / WHATSAPP</label>
                            {{ salon_form.phone }}
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label fw-bold small text-secondary">DIRECCIÓN FÍSICA</label>
                        {{ salon_form.address }}
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label fw-bold small text-secondary">INSTAGRAM (Sin @)</label>
                        <div class="input-group">
                            <span class="input-group-text bg-light border-end-0">@</span>
                            {{ salon_form.instagram }}
                        </div>
                    </div>
                    
                    <div class="alert alert-warning border-0 small mt-4">
                        <i class="bi bi-cash-coin me-1 fw-bold"></i> <strong>Política de Abonos:</strong>
                        Actualmente el sistema cobra el 50% de abono automáticamente para confirmar reservas.
                    </div>
                </div>
            </div>
        </div>

        <div class="col-lg-7">
            <div class="card shadow-lg border-0 rounded-4 overflow-hidden h-100">
                <div class="card-header bg-white py-3 border-bottom">
                    <h5 class="mb-0 fw-bold text-dark"><i class="bi bi-calendar-week me-2"></i> Días Laborales</h5>
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover mb-0 align-middle">
                            <thead class="bg-light">
                                <tr>
                                    <th class="ps-4 py-3">Día</th>
                                    <th class="text-center">Estado</th>
                                    <th class="pe-4 text-end">Acción</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="ps-4 fw-bold text-secondary">Lunes</td>
                                    <td class="text-center">
                                        <span class="badge bg-success rounded-pill status-text" id="status-monday">ABIERTO</span>
                                    </td>
                                    <td class="pe-4 text-end">
                                        <div class="form-check form-switch d-inline-block">
                                            {{ schedule_form.monday_open }}
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="ps-4 fw-bold text-secondary">Martes</td>
                                    <td class="text-center">
                                        <span class="badge bg-success rounded-pill status-text" id="status-tuesday">ABIERTO</span>
                                    </td>
                                    <td class="pe-4 text-end">
                                        <div class="form-check form-switch d-inline-block">
                                            {{ schedule_form.tuesday_open }}
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="ps-4 fw-bold text-secondary">Miércoles</td>
                                    <td class="text-center">
                                        <span class="badge bg-success rounded-pill status-text" id="status-wednesday">ABIERTO</span>
                                    </td>
                                    <td class="pe-4 text-end">
                                        <div class="form-check form-switch d-inline-block">
                                            {{ schedule_form.wednesday_open }}
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="ps-4 fw-bold text-secondary">Jueves</td>
                                    <td class="text-center">
                                        <span class="badge bg-success rounded-pill status-text" id="status-thursday">ABIERTO</span>
                                    </td>
                                    <td class="pe-4 text-end">
                                        <div class="form-check form-switch d-inline-block">
                                            {{ schedule_form.thursday_open }}
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="ps-4 fw-bold text-secondary">Viernes</td>
                                    <td class="text-center">
                                        <span class="badge bg-success rounded-pill status-text" id="status-friday">ABIERTO</span>
                                    </td>
                                    <td class="pe-4 text-end">
                                        <div class="form-check form-switch d-inline-block">
                                            {{ schedule_form.friday_open }}
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="ps-4 fw-bold text-secondary">Sábado</td>
                                    <td class="text-center">
                                        <span class="badge bg-success rounded-pill status-text" id="status-saturday">ABIERTO</span>
                                    </td>
                                    <td class="pe-4 text-end">
                                        <div class="form-check form-switch d-inline-block">
                                            {{ schedule_form.saturday_open }}
                                        </div>
                                    </td>
                                </tr>
                                <tr class="bg-light bg-opacity-50">
                                    <td class="ps-4 fw-bold text-danger">Domingo</td>
                                    <td class="text-center">
                                        <span class="badge bg-secondary rounded-pill status-text" id="status-sunday">CERRADO</span>
                                    </td>
                                    <td class="pe-4 text-end">
                                        <div class="form-check form-switch d-inline-block">
                                            {{ schedule_form.sunday_open }}
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="card-footer bg-white p-4">
                    <button type="submit" class="btn btn-dark btn-lg w-100 rounded-pill fw-bold shadow">
                        <i class="bi bi-save2 me-2"></i> Guardar Configuración
                    </button>
                </div>
            </div>
        </div>
    </form>
</div>

<script>
    document.addEventListener("DOMContentLoaded", function() {
        // 1. Estilizar checkboxes de Django
        var switches = document.querySelectorAll('.form-check-input');
        switches.forEach(function(el) {
            el.classList.add('form-check-input');
            el.setAttribute('role', 'switch');
            
            // Evento para cambiar el texto de ABIERTO/CERRADO en tiempo real
            el.addEventListener('change', function() {
                updateStatus(this);
            });
            // Inicializar estado
            updateStatus(el);
        });

        function updateStatus(input) {
            // Buscamos el badge en la misma fila
            var row = input.closest('tr');
            var badge = row.querySelector('.status-text');
            
            if (input.checked) {
                badge.textContent = 'ABIERTO';
                badge.classList.remove('bg-secondary');
                badge.classList.add('bg-success');
            } else {
                badge.textContent = 'CERRADO';
                badge.classList.remove('bg-success');
                badge.classList.add('bg-secondary');
            }
        }
    });
</script>
{% endblock %}
"""

def restaurar_legado():
    print("🏛️ Restaurando Views.py con lógica de negocio...")
    with open(VIEWS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_VIEWS)

    print("🏺 Reconstruyendo owner_settings.html con diseño del backup (Cards & Shadows)...")
    with open(SETTINGS_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_HTML)

    print("✅ ¡Restauración completa! Diseño clásico con motor moderno.")

if __name__ == "__main__":
    restaurar_legado()