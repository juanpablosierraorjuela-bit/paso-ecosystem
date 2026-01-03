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
from .models import Salon, Service, Booking, Employee, Schedule, OpeningHours

User = get_user_model()

def get_salon(user): return Salon.objects.filter(owner=user).first()

def check_expired_bookings():
    try:
        limit = timezone.now() - timedelta(minutes=30)
        Booking.objects.filter(status='pending_payment', created_at__lt=limit).update(status='expired')
    except: pass

def get_available_slots(employee, check_date, duration=60):
    check_expired_bookings()
    day_idx = check_date.weekday()
    # Lógica simplificada de horarios (asumiendo que existen)
    try:
        sched = Schedule.objects.filter(employee=employee, day_of_week=day_idx, is_active=True).first()
        if not sched: return []
        slots = []
        current = datetime.combine(check_date, sched.start_time)
        limit = datetime.combine(check_date, sched.end_time)

        # Filtro hoy
        if check_date == date.today():
            if current < datetime.now() + timedelta(minutes=30):
                current = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        while current + timedelta(minutes=duration) <= limit:
            # Aquí iría el check de colisiones real
            slots.append(current.strftime('%H:%M'))
            current += timedelta(minutes=30)
        return slots
    except: return []

# WIZARD
def booking_wizard_start(request): 
    sid = request.POST.getlist('service_ids')
    if not sid: return redirect('home')
    request.session['booking']={'salon_slug':request.POST.get('salon_slug'), 'service_ids':sid}
    return redirect('booking_step_employee')

def booking_step_employee(request):
    d = request.session.get('booking')
    s = get_object_or_404(Salon, slug=d['salon_slug'])
    if request.method == 'POST':
        request.session['booking']['emp_id'] = request.POST.get('employee_id')
        request.session.modified = True
        return redirect('booking_step_datetime')
    return render(request, 'booking_wizard_employee.html', {'salon': s, 'employees': Employee.objects.filter(salon=s)})

def booking_step_datetime(request):
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    date_str = request.GET.get('date', date.today().isoformat())
    return render(request, 'booking_wizard_datetime.html', {'salon': s, 'slots': ['09:00', '10:00', '11:00'], 'selected_date': date_str})

def booking_step_contact(request):
    if request.method == 'POST':
        request.session['booking'].update({'date': request.POST.get('date'), 'time': request.POST.get('time')})
        request.session.modified = True
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    total = sum(sv.price for sv in Service.objects.filter(id__in=d['service_ids']))
    porcentaje = Decimal(s.deposit_percentage) / Decimal(100)
    return render(request, 'booking_contact.html', {'salon': s, 'total': total, 'abono': total * porcentaje, 'porcentaje': s.deposit_percentage})

def booking_create(request):
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    email = request.POST['customer_email']
    u, created = User.objects.get_or_create(email=email, defaults={'username': email})
    if created: u.set_password('123456'); u.save()
    login(request, u, backend='django.contrib.auth.backends.ModelBackend')

    emp = Employee.objects.filter(salon=s).first() # Fallback simple
    for sid in d['service_ids']:
        Booking.objects.create(salon=s, service_id=sid, employee=emp, customer_name=request.POST['customer_name'], customer_email=email, customer_phone=request.POST['customer_phone'], date=d['date'], time=d['time'])

    del request.session['booking']
    return redirect('client_dashboard')

# DASHBOARDS
@login_required
def client_dashboard(request):
    check_expired_bookings()
    bookings = Booking.objects.filter(customer_email=request.user.email)
    citas = []
    for b in bookings:
        precio = b.service.price
        porcentaje = Decimal(b.salon.deposit_percentage) / Decimal(100)
        abono = precio * porcentaje
        msg = f"Hola {b.salon.name}, pago cita #{b.id}. Abono: ${abono:,.0f}."
        citas.append({'obj': b, 'abono': abono, 'pendiente': precio - abono, 'wa_link': f"https://wa.me/{b.salon.phone}?text={urllib.parse.quote(msg)}"})
    return render(request, 'client_dashboard.html', {'citas': citas})

@login_required
def owner_dashboard(request):
    return render(request, 'dashboard/owner_dashboard.html', {'salon': get_salon(request.user)})

@login_required
def booking_confirm_payment(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id)
    b.status = 'confirmed'; b.save()
    return redirect('owner_dashboard')

# AUTH
def saas_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid(): login(request, form.get_user()); return redirect('client_dashboard')
    return render(request, 'registration/login.html', {'form': UserLoginForm()})

def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            u = User.objects.create_user(username=form.cleaned_data['email'], email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            Salon.objects.create(owner=u, name=form.cleaned_data['nombre_negocio'], city=form.cleaned_data['ciudad'], phone=form.cleaned_data['whatsapp'])
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('owner_dashboard')
    return render(request, 'registration/register_owner.html', {'form': OwnerRegistrationForm()})

def home(request): return render(request, 'home.html')
def marketplace(request): return render(request, 'marketplace.html', {'salons': Salon.objects.all()})
def salon_detail(request, slug): 
    s = get_object_or_404(Salon, slug=slug)
    return render(request, 'salon_detail.html', {'salon': s, 'services': Service.objects.filter(salon=s)})
def saas_logout(request): logout(request); return redirect('home')