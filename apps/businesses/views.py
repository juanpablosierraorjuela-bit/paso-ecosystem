from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import urllib.parse
from .forms import *
from .models import Salon, Service, Booking, Employee

User = get_user_model()

# --- UTILIDADES ---
def get_salon(user): return Salon.objects.filter(owner=user).first()

def check_expired_bookings():
    try:
        limit = timezone.now() - timedelta(minutes=60)
        Booking.objects.filter(status='pending_payment', created_at__lt=limit).update(status='expired')
    except: pass

def get_available_slots(employee, check_date, duration=60):
    check_expired_bookings()
    salon = employee.salon
    start_time = salon.open_time
    end_time = salon.close_time
    slots = []
    current = datetime.combine(check_date, start_time)
    limit = datetime.combine(check_date, end_time)

    if check_date == date.today():
        now_buffer = datetime.now() + timedelta(minutes=30)
        if current < now_buffer:
            minute = now_buffer.minute
            new_start = now_buffer.replace(minute=30 if minute < 30 else 0, second=0, microsecond=0)
            if minute >= 30: new_start += timedelta(hours=1)
            current = new_start

    bookings = Booking.objects.filter(employee=employee, date=check_date).exclude(status__in=['cancelled', 'expired'])
    busy_times = []
    for b in bookings:
        start = datetime.combine(check_date, b.time)
        end = start + timedelta(minutes=b.service.duration_minutes)
        busy_times.append((start, end))

    if employee.lunch_start and employee.lunch_end:
        l_start = datetime.combine(check_date, employee.lunch_start)
        l_end = datetime.combine(check_date, employee.lunch_end)
        busy_times.append((l_start, l_end))

    while current + timedelta(minutes=duration) <= limit:
        service_end = current + timedelta(minutes=duration)
        is_free = True
        for busy_start, busy_end in busy_times:
            if (current < busy_end) and (service_end > busy_start):
                is_free = False
                break
        if is_free: slots.append(current.strftime('%H:%M'))
        current += timedelta(minutes=30)
    return slots

# --- MARKETPLACE & LANDING ---
def home(request): return render(request, 'home.html')

def marketplace(request):
    city = request.GET.get('city')
    salons = Salon.objects.all()
    if city: salons = salons.filter(city__iexact=city)
    cities = Salon.objects.values_list('city', flat=True).distinct().order_by('city')
    return render(request, 'marketplace.html', {'salons': salons, 'cities': cities, 'current_city': city})

def salon_detail(request, slug):
    s = get_object_or_404(Salon, slug=slug)
    return render(request, 'salon_detail.html', {'salon': s, 'services': s.services.all()})

# --- FLUJO DE RESERVA ---
def booking_wizard_start(request): 
    sid = request.POST.getlist('service_ids')
    if not sid:
        messages.error(request, "⚠️ Selecciona al menos un servicio.")
        return redirect('salon_detail', slug=request.POST.get('salon_slug'))
    request.session['booking'] = {'salon_slug': request.POST.get('salon_slug'), 'service_ids': sid}
    return redirect('booking_step_employee')

def booking_step_employee(request):
    d = request.session.get('booking')
    s = get_object_or_404(Salon, slug=d['salon_slug'])
    if request.method == 'POST':
        request.session['booking']['emp_id'] = request.POST.get('employee_id')
        request.session.modified = True
        return redirect('booking_step_datetime')
    return render(request, 'booking_wizard_employee.html', {'salon': s, 'employees': s.employees.filter(is_active=True)})

def booking_step_datetime(request):
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    date_str = request.GET.get('date', date.today().isoformat())
    check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    services = Service.objects.filter(id__in=d['service_ids'])
    total_duration = sum(srv.duration_minutes for srv in services)

    emp_id = d.get('emp_id')
    slots = []
    if emp_id and emp_id != 'any':
        emp = Employee.objects.get(id=emp_id)
        slots = get_available_slots(emp, check_date, total_duration)
    else:
        all_slots = set()
        for emp in s.employees.filter(is_active=True):
            emp_slots = get_available_slots(emp, check_date, total_duration)
            all_slots.update(emp_slots)
        slots = sorted(list(all_slots))

    return render(request, 'booking_wizard_datetime.html', {'salon': s, 'slots': slots, 'selected_date': date_str, 'duration': total_duration})

def booking_step_contact(request):
    if request.method == 'POST':
        request.session['booking'].update({'date': request.POST.get('date'), 'time': request.POST.get('time')})
        request.session.modified = True
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    services = Service.objects.filter(id__in=d['service_ids'])
    total = sum(srv.price for srv in services)
    porcentaje = Decimal(s.deposit_percentage) / Decimal(100)
    abono = total * porcentaje
    return render(request, 'booking_contact.html', {'salon': s, 'services': services, 'total': total, 'abono': abono, 'porcentaje': s.deposit_percentage})

def booking_create(request):
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    email = request.POST['customer_email']
    u, created = User.objects.get_or_create(email=email, defaults={'username': email})
    if created: u.set_password('123456'); u.save()
    login(request, u, backend='django.contrib.auth.backends.ModelBackend')

    emp_id = d.get('emp_id')
    emp = Employee.objects.get(id=emp_id) if (emp_id and emp_id != 'any') else s.employees.filter(is_active=True).first()

    for sid in d['service_ids']:
        Booking.objects.create(
            salon=s, service_id=sid, employee=emp, customer_name=request.POST['customer_name'],
            customer_email=email, customer_phone=request.POST['customer_phone'], date=d['date'], time=d['time']
        )
    del request.session['booking']
    messages.success(request, "¡Reserva Creada! Gestiona tu pago ahora.")
    return redirect('client_dashboard')

# --- PANELES ---
@login_required
def client_dashboard(request):
    check_expired_bookings()
    bookings = Booking.objects.filter(customer_email=request.user.email).order_by('-date', '-time')
    citas_data = []
    for b in bookings:
        precio = b.service.price
        porcentaje = Decimal(b.salon.deposit_percentage) / Decimal(100)
        abono = precio * porcentaje
        pendiente = precio - abono
        msg = f"👋 Hola {b.salon.name}, soy {b.customer_name}.\n📅 Cita #{b.id} el {b.date} a las {b.time}.\n💰 Total: ${precio:,.0f}\n✅ Abono a pagar: ${abono:,.0f}"
        wa_link = f"https://wa.me/{b.salon.phone}?text={urllib.parse.quote(msg)}"
        citas_data.append({'obj': b, 'abono': abono, 'pendiente': pendiente, 'wa_link': wa_link})
    return render(request, 'client_dashboard.html', {'citas': citas_data})

@login_required
def owner_dashboard(request):
    s = get_salon(request.user)
    if not s: return redirect('home')
    check_expired_bookings()
    bookings = Booking.objects.filter(salon=s).order_by('-created_at')
    return render(request, 'dashboard/owner_dashboard.html', {'salon': s, 'bookings': bookings})

@login_required
def booking_confirm_payment(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id)
    if b.salon.owner == request.user:
        b.status = 'confirmed'; b.save()
        messages.success(request, f"Pago confirmado para cita #{b.id}")
    return redirect('owner_dashboard')

# --- AUTH ACTUALIZADO (Con Address y link de Instagram) ---
def saas_login(request):
    if request.user.is_authenticated:
        if Salon.objects.filter(owner=request.user).exists(): return redirect('owner_dashboard')
        return redirect('client_dashboard')
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if Salon.objects.filter(owner=request.user).exists(): return redirect('owner_dashboard')
            return redirect('client_dashboard')
    else: form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})

def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                u = User.objects.create_user(
                    username=form.cleaned_data['email'], email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'], first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )
                u.role = 'ADMIN'; u.save()

                # Crear Link de Instagram
                ig_user = form.cleaned_data['instagram']
                ig_link = f"https://instagram.com/{ig_user}" if ig_user else ""

                Salon.objects.create(
                    owner=u,
                    name=form.cleaned_data['nombre_negocio'],
                    city=form.cleaned_data['ciudad'],
                    address=form.cleaned_data['direccion'],
                    phone=form.cleaned_data['whatsapp'],
                    instagram_link=ig_link
                )
                login(request, u, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('owner_dashboard')
    else:
        form = OwnerRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

def saas_logout(request): logout(request); return redirect('home')