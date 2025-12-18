from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.db import transaction
from django.contrib import messages

from apps.businesses.models import Salon, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    salons = Salon.objects.all().order_by('-id')
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """
    Registro Inteligente: Redirige según el rol del usuario.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # --- CEREBRO DE REDIRECCIÓN ---
            if user.role == 'OWNER':
                # Si es dueño, LO OBLIGAMOS a crear su salón de inmediato
                return redirect('create_salon')
            elif user.role == 'EMPLOYEE':
                # Si es empleado, va a su configuración
                return redirect('employee_settings')
            else:
                # Si es cliente, va al home a buscar servicios
                return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    Panel Inteligente: Muestra lo que cada usuario necesita ver.
    """
    user = request.user

    # 1. LOGICA DE DUEÑO
    if user.role == 'OWNER':
        if hasattr(user, 'salon'):
            # Si ya tiene salón, ve su panel de control
            return render(request, 'dashboard/index.html', {'salon': user.salon})
        else:
            # Si es dueño pero NO tiene salón, lo mandamos a crearlo
            return redirect('create_salon')

    # 2. LOGICA DE EMPLEADO
    if user.role == 'EMPLOYEE':
        return redirect('employee_settings')

    # 3. LOGICA DE CLIENTE
    # Muestra sus próximas citas
    bookings = Booking.objects.filter(customer=user).order_by('-start_time')
    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def create_salon_view(request):
    if hasattr(request.user, 'salon'):
        return redirect('dashboard')

    if request.method == 'POST':
        form = SalonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                
                # Aseguramos que el usuario tenga el rol correcto
                request.user.role = 'OWNER'
                request.user.save()

            messages.success(request, "¡Tu negocio ha sido creado! Ahora agrega tus servicios.")
            return redirect('manage_services') # Lo llevamos directo a crear servicios
    else:
        form = SalonCreateForm()
        
    return render(request, 'dashboard/create_salon.html', {'form': form})

# Views de soporte
def accept_invite_view(request): return redirect('dashboard')
def employee_join_view(request): return redirect('dashboard')