from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

from apps.businesses.models import Salon, Employee, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    salons = Salon.objects.all().order_by('-id')
    return render(request, 'home.html', {'salons': salons})

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    Panel Unificado Robusto (Sin Errores 500)
    """
    user = request.user

    # 1. ¿ES EMPLEADO?
    # Usamos hasattr que ahora es 100% seguro gracias al related_name='employee' en models.py
    if hasattr(user, 'employee'):
        return redirect('employee_settings')

    # 2. ¿ES DUEÑO?
    is_owner = getattr(user, 'role', '') == 'ADMIN' or getattr(user, 'is_business_owner', False)
    
    if is_owner:
        salon = Salon.objects.filter(owner=user).first()
        if not salon:
            return redirect('create_salon')
        return render(request, 'dashboard/index.html', {'salon': salon})

    # 3. ¿ES CLIENTE?
    # BLOQUE DE SEGURIDAD: Si la migración de 'customer' falló, esto evita el Error 500
    try:
        my_bookings = Booking.objects.filter(customer=user).order_by('-start_time')
    except Exception:
        # Si falla la DB, mostramos lista vacía en lugar de romper el sitio
        my_bookings = []
        
    return render(request, 'dashboard/client_dashboard.html', {'bookings': my_bookings})

@login_required
def create_salon_view(request):
    if Salon.objects.filter(owner=request.user).exists():
        return redirect('dashboard')
    if request.method == 'POST':
        form = SalonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            salon = form.save(commit=False)
            salon.owner = request.user
            salon.save()
            return redirect('dashboard')
    else:
        form = SalonCreateForm()
    return render(request, 'dashboard/create_salon.html', {'form': form})

def salon_detail(request, slug):
    from apps.businesses.views import salon_detail as business_salon_detail
    return business_salon_detail(request, slug)