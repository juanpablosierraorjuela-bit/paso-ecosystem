import os
import subprocess

# -----------------------------------------------------------------------------
# 1. MEJORAR REGISTER_OWNER.HTML (Feedback de errores explícito)
# -----------------------------------------------------------------------------
reg_path = os.path.join('templates', 'registration', 'register_owner.html')
print(f" Mejorando feedback en {reg_path}...")

new_reg_code = r"""{% extends 'master.html' %}
{% load static %}

{% block content %}
<style>
    body { background-color: #f8f9fa; }
    .register-container {
        background: white;
        border-radius: 30px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        overflow: hidden;
        min-height: 80vh;
    }
    .register-sidebar {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 4rem;
        position: relative;
    }
    .gold-accent { color: #d4af37; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; font-size: 0.9rem; }
    .form-control { border-radius: 12px; padding: 0.8rem 1rem; border: 1px solid #e9ecef; }
    .form-select { border-radius: 12px; padding: 0.8rem 1rem; border: 1px solid #e9ecef; }
    .btn-register { background: #000; color: white; padding: 1rem; border-radius: 50px; width: 100%; font-weight: bold; transition: 0.3s; }
    .btn-register:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); color: #d4af37; }
    .error-msg { font-size: 0.75rem; color: #dc3545; margin-top: 4px; font-weight: 600; }
</style>

<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-xl-11">
            <div class="row g-0 register-container">
                <div class="col-lg-5 register-sidebar d-none d-lg-flex text-center text-lg-start">
                    <div style="z-index: 2;">
                        <div class="gold-accent mb-3">Paso Ecosystem</div>
                        <h1 class="display-4 fw-bold mb-4">Potencia tu<br>Marca.</h1>
                        <p class="lead text-white-50 mb-5">Gestión inteligente para negocios que quieren crecer.</p>
                    </div>
                </div>

                <div class="col-lg-7 p-5 bg-white">
                    <h3 class="fw-bold mb-1 text-dark">Crear Cuenta de Negocio</h3>
                    <p class="text-muted small mb-4">Únete a la revolución digital.</p>

                    <form method="post">
                        {% csrf_token %}
                        
                        {% if form.non_field_errors %}
                            <div class="alert alert-danger border-0 shadow-sm rounded-3 mb-4">
                                <i class="fas fa-exclamation-triangle me-2"></i> {{ form.non_field_errors.0 }}
                            </div>
                        {% endif %}

                        <h6 class="fw-bold text-muted text-uppercase small border-bottom pb-2 mb-3">Datos de Acceso</h6>
                        <div class="row g-3 mb-2">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Usuario</label>
                                {{ form.username }}
                                {% if form.username.errors %}<div class="error-msg">{{ form.username.errors.0 }}</div>{% endif %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Email</label>
                                {{ form.email }}
                                {% if form.email.errors %}<div class="error-msg">{{ form.email.errors.0 }}</div>{% endif %}
                            </div>
                        </div>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Contraseña</label>
                                {{ form.password1 }}
                                {% if form.password1.errors %}<div class="error-msg">{{ form.password1.errors.0 }}</div>{% endif %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Confirmar</label>
                                {{ form.password2 }}
                                {% if form.password2.errors %}<div class="error-msg">{{ form.password2.errors.0 }}</div>{% endif %}
                            </div>
                        </div>

                        <h6 class="fw-bold text-muted text-uppercase small border-bottom pb-2 mb-3">Tu Negocio</h6>
                        <div class="mb-3">
                            <label class="form-label small fw-bold">Nombre del Establecimiento</label>
                            {{ form.salon_name }}
                        </div>
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Ciudad</label>
                                {{ form.city }}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Dirección</label>
                                {{ form.address }}
                            </div>
                        </div>
                        <div class="mb-4">
                            <label class="form-label small fw-bold text-success"><i class="fab fa-whatsapp me-1"></i> WhatsApp de Reservas</label>
                            {{ form.phone }}
                            <div class="form-text small">A este número llegarán los comprobantes de pago.</div>
                        </div>

                        <button type="submit" class="btn btn-register">
                            CREAR CUENTA <i class="fas fa-rocket ms-2"></i>
                        </button>
                    </form>
                    <div class="text-center mt-4 border-top pt-3">
                        <p class="small text-muted">¿Ya tienes cuenta? <a href="{% url 'saas_login' %}" class="fw-bold text-dark">Iniciar Sesión</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
with open(reg_path, 'w', encoding='utf-8') as f:
    f.write(new_reg_code)

# -----------------------------------------------------------------------------
# 2. ACTUALIZAR VIEWS.PY (Lógica de Reserva Blindada + Cliente Automático)
# -----------------------------------------------------------------------------
views_path = os.path.join('apps', 'businesses', 'views.py')
print(f" Implantando cerebro inteligente en {views_path}...")

new_views_code = r"""from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import SalonRegistrationForm, SalonSettingsForm, ServiceForm, EmployeeForm, EmployeeScheduleForm
from apps.core_saas.models import User
from .models import Salon, Service, Employee, Booking, EmployeeSchedule
from datetime import datetime, timedelta
import pytz
from django.utils import timezone
import urllib.parse
from django.core.exceptions import ObjectDoesNotExist

# --- HELPERS INTELIGENTES ---
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

        # LÓGICA INTELIGENTE: Duración del servicio vs Cierre
        service_duration = timedelta(minutes=service.duration + service.buffer_time)
        current = work_start
        
        bogota_tz = pytz.timezone("America/Bogota")
        now_bogota = datetime.now(bogota_tz)

        while current + service_duration <= work_end:
            # Verificar si ya pasó la hora
            current_aware = pytz.timezone("America/Bogota").localize(current)
            if current_aware <= now_bogota:
                current += timedelta(minutes=30)
                continue

            # Verificar choques con otras citas
            collision = Booking.objects.filter(
                employee=employee, 
                status__in=["PENDING_PAYMENT", "VERIFIED"], 
                date_time__lt=current + service_duration, 
                end_time__gt=current
            ).exists()

            if not collision: 
                slots.append(current.strftime("%H:%M"))
            
            current += timedelta(minutes=30)
            
    except Exception as e:
        print(f"Error slots: {e}")
        return []
    return slots

# --- FLOW DE RESERVAS ---

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
    if request.method == "POST":
        request.session["booking_employee"] = request.POST.get("employee_id")
    
    employee_id = request.session.get("booking_employee")
    service_id = request.session.get("booking_service")
    
    if not (employee_id and service_id):
        return redirect("marketplace")
    
    employee = get_object_or_404(Employee, id=employee_id)
    service = get_object_or_404(Service, id=service_id)
    
    today = datetime.now().date()
    selected_date_str = request.GET.get("date", str(today))
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
        selected_date = today
        selected_date_str = str(today)

    slots = get_available_slots(employee, datetime.combine(selected_date, datetime.min.time()), service)
    
    return render(request, "booking/step_calendar.html", {
        "employee": employee, "service": service, "slots": slots,
        "selected_date": selected_date_str, "today": str(today)
    })

def booking_step_confirm(request):
    # BLINDAJE CONTRA "DATOS INCOMPLETOS"
    if request.method == "POST":
        # Guardamos lo que viene del calendario
        request.session["booking_time"] = request.POST.get("time")
        request.session["booking_date"] = request.POST.get("date_selected")
    
    date_str = request.session.get("booking_date")
    time_str = request.session.get("booking_time")
    service_id = request.session.get("booking_service")

    # Si falta algo, devolvemos al calendario con un mensaje claro
    if not (date_str and time_str and service_id):
        messages.error(request, "Por favor selecciona una fecha y hora.")
        return redirect("booking_step_calendar")

    service = get_object_or_404(Service, id=service_id)
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except:
        date_obj = datetime.now()

    return render(request, "booking/step_confirm.html", {
        "service": service, "time": time_str, "date": date_str, "date_pretty": date_obj
    })

def booking_create(request):
    if request.method == "POST":
        # Recuperar datos de sesión
        salon_id = request.session.get("booking_salon")
        service_id = request.session.get("booking_service")
        employee_id = request.session.get("booking_employee")
        time_str = request.session.get("booking_time")
        date_str = request.session.get("booking_date")
        
        customer_name = request.POST.get("customer_name")
        customer_phone = request.POST.get("customer_phone")
        
        if not (salon_id and service_id and employee_id and time_str and date_str):
            messages.error(request, "La sesión expiró. Intenta de nuevo.")
            return redirect("marketplace")
            
        try:
            salon = get_object_or_404(Salon, id=salon_id)
            service = get_object_or_404(Service, id=service_id)
            employee = get_object_or_404(Employee, id=employee_id)
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            start_datetime = datetime.combine(date_obj, time_obj)
            
            # --- CLIENTE AUTOMÁTICO (MAGIC FEATURE) ---
            # Si el usuario no está logueado, buscamos si existe por teléfono o creamos uno
            booking_user = None
            if request.user.is_authenticated:
                booking_user = request.user
            else:
                # Buscar por username (usamos el teléfono como ID único)
                user_qs = User.objects.filter(username=customer_phone)
                if user_qs.exists():
                    booking_user = user_qs.first()
                    # Opcional: Loguearlo automáticamente
                    login(request, booking_user)
                else:
                    # Crear nuevo cliente
                    booking_user = User.objects.create_user(
                        username=customer_phone,
                        email=f"{customer_phone}@cliente.com", # Email temporal
                        password=customer_phone, # La clave es su teléfono inicialmente
                        role="CLIENT",
                        first_name=customer_name
                    )
                    login(request, booking_user)
                    messages.info(request, f"¡Cuenta creada! Tu usuario y clave es tu teléfono: {customer_phone}")

            # Crear Reserva
            total_price = service.price
            deposit_amount = total_price * (salon.deposit_percentage / 100)
            
            booking = Booking.objects.create(
                salon=salon, service=service, employee=employee, 
                customer_name=customer_name, customer_phone=customer_phone, 
                date_time=start_datetime, total_price=total_price, 
                deposit_amount=deposit_amount, status="PENDING_PAYMENT"
            )
            return redirect("booking_success", booking_id=booking.id)
            
        except Exception as e:
            print(f"Error Reserva: {e}")
            messages.error(request, "Ocurrió un error. Intenta otro horario.")
            return redirect("booking_step_calendar")
            
    return redirect("marketplace")

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    salon = booking.salon
    
    # Cronómetro 60 mins
    created_at = booking.created_at
    if timezone.is_naive(created_at):
        created_at = timezone.make_aware(created_at, pytz.timezone("America/Bogota"))
    now = timezone.now()
    elapsed = (now - created_at).total_seconds()
    time_left_seconds = max(0, 3600 - elapsed)
    is_expired = time_left_seconds <= 0

    remaining = booking.total_price - booking.deposit_amount
    total_fmt = "${:,.0f}".format(booking.total_price)
    deposit_fmt = "${:,.0f}".format(booking.deposit_amount)
    
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
    
    return render(request, "booking/success.html", {
        "booking": booking, "whatsapp_url": whatsapp_url, 
        "deposit_fmt": deposit_fmt, "time_left_seconds": int(time_left_seconds), 
        "is_expired": is_expired
    })

# --- VISTAS DASHBOARD & AUTH (Mantenemos lo que funciona) ---
@login_required
def owner_dashboard(request): return render(request, "dashboard/owner_dashboard.html")
@login_required
def employee_dashboard(request): 
    employee = request.user.employee_profile
    bookings = Booking.objects.filter(employee=employee).order_by("date_time")
    return render(request, "employee_dashboard.html", {"employee": employee, "bookings": bookings})
@login_required
def employee_schedule(request):
    employee = request.user.employee_profile
    schedule, created = EmployeeSchedule.objects.get_or_create(employee=employee)
    if request.method == "POST":
        form = EmployeeScheduleForm(request.POST, instance=schedule, salon=employee.salon)
        if form.is_valid(): form.save(); messages.success(request, "Horario guardado."); return redirect("employee_schedule")
    else: form = EmployeeScheduleForm(instance=schedule, salon=employee.salon)
    return render(request, "dashboard/employee_schedule.html", {"form": form, "salon": employee.salon})

def saas_login(request):
    if request.method == "POST":
        u = request.POST.get("username"); p = request.POST.get("password")
        user = authenticate(username=u, password=p)
        if user: login(request, user); return redirect("owner_dashboard") if user.role == "OWNER" else redirect("employee_dashboard")
        else: messages.error(request, "Credenciales inválidas")
    return render(request, "registration/login.html")
def saas_logout(request): logout(request); return redirect("home")

@transaction.atomic
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
                owner=user, name=form.cleaned_data["salon_name"], city=form.cleaned_data["city"],
                address=form.cleaned_data["address"], whatsapp_number=form.cleaned_data["phone"],
                instagram_link=form.cleaned_data.get("instagram_link", ""), maps_link=form.cleaned_data.get("maps_link", "")
            )
            login(request, user); return redirect("owner_dashboard")
    else: form = SalonRegistrationForm()
    return render(request, "registration/register_owner.html", {"form": form})

# --- GENERICAS ---
def home(request): return render(request, "home.html")
def marketplace(request):
    q = request.GET.get("q", ""); city = request.GET.get("city", "")
    salons = Salon.objects.all()
    if q: salons = salons.filter(name__icontains=q)
    if city: salons = salons.filter(city=city)
    return render(request, "marketplace.html", {"salons": salons, "cities": Salon.objects.values_list("city", flat=True).distinct()})
def salon_detail(request, pk): return render(request, "salon_detail.html", {"salon": get_object_or_404(Salon, pk=pk)})
def landing_businesses(request): return render(request, "landing_businesses.html")
@login_required
def owner_services(request): return render(request, "dashboard/owner_services.html", {"services": request.user.salon.services.all()})
@login_required
def service_create(request):
    if request.method=="POST": 
        f=ServiceForm(request.POST); 
        if f.is_valid(): s=f.save(commit=False); s.salon=request.user.salon; s.save(); return redirect("owner_services")
    return render(request, "dashboard/service_form.html", {"form": ServiceForm()})
@login_required
def service_update(request, pk):
    s=get_object_or_404(Service, pk=pk, salon=request.user.salon)
    if request.method=="POST": f=ServiceForm(request.POST, instance=s); f.save(); return redirect("owner_services")
    return render(request, "dashboard/service_form.html", {"form": ServiceForm(instance=s)})
@login_required
def service_delete(request, pk):
    s=get_object_or_404(Service, pk=pk, salon=request.user.salon); 
    if request.method=="POST": s.delete(); return redirect("owner_services")
    return render(request, "dashboard/service_confirm_delete.html", {"object": s})
@login_required
def owner_employees(request): return render(request, "dashboard/owner_employees.html", {"employees": request.user.salon.employees.all()})
@login_required
def employee_create(request):
    if request.method=="POST":
        f=EmployeeForm(request.POST)
        if f.is_valid():
            u=None; un=f.cleaned_data.get("username"); pw=f.cleaned_data.get("password")
            if un and pw: u=User.objects.create_user(username=un, password=pw, role="EMPLOYEE")
            e=f.save(commit=False); e.salon=request.user.salon; e.user=u; e.save(); EmployeeSchedule.objects.create(employee=e)
            return redirect("owner_employees")
    return render(request, "dashboard/employee_form.html", {"form": EmployeeForm()})
@login_required
def employee_update(request, pk):
    e=get_object_or_404(Employee, pk=pk, salon=request.user.salon)
    if request.method=="POST": f=EmployeeForm(request.POST, instance=e); f.save(); return redirect("owner_employees")
    return render(request, "dashboard/employee_form.html", {"form": EmployeeForm(instance=e)})
@login_required
def employee_delete(request, pk):
    e=get_object_or_404(Employee, pk=pk, salon=request.user.salon)
    if request.method=="POST": 
        if e.user: e.user.delete()
        e.delete(); return redirect("owner_employees")
    return render(request, "dashboard/employee_confirm_delete.html", {"object": e})
@login_required
def verify_booking(request, pk):
    b=get_object_or_404(Booking, pk=pk, salon=request.user.salon); b.status="VERIFIED"; b.save(); messages.success(request, "Verificada"); return redirect("owner_dashboard")
@login_required
def owner_settings(request):
    s=request.user.salon
    if request.method=="POST": f=SalonSettingsForm(request.POST, instance=s); f.save(); messages.success(request, "Guardado"); return redirect("owner_dashboard")
    return render(request, "dashboard/owner_settings.html", {"form": SalonSettingsForm(instance=s)})
"""
with open(views_path, 'w', encoding='utf-8') as f:
    f.write(new_views_code)

# -----------------------------------------------------------------------------
# 3. SUBIR A PRODUCCIÓN
# -----------------------------------------------------------------------------
print(" Ejecutando Plan Maestro de Lanzamiento...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Master Upgrade: Auto-Cliente, Reservas Blindadas y Registro Pro"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print(" ¡SISTEMA ACTUALIZADO! Espera 3 minutos y serás imparable.")
except Exception as e:
    print(f" Error Git: {e}")