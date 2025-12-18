from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
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
    REGISTRO INTELIGENTE:
    Detecta qué eligió el usuario y lo manda a su lugar correcto.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # --- CEREBRO DE DIRECCIONAMIENTO ---
            if user.role == 'OWNER':
                # Es dueño, pero... ¿ya creó su negocio? (Al registrarse obvio que no)
                return redirect('create_salon')
            
            elif user.role == 'EMPLOYEE':
                # Es empleado, va a configurar su horario
                return redirect('employee_settings')
            
            else:
                # Es cliente (CLIENT), va al inicio a buscar peluquerías
                return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    PANEL INTELIGENTE:
    Si entra un dueño, ve métricas. Si entra cliente, ve citas.
    """
    user = request.user

    # 1. CASO DUEÑO
    if user.role == 'OWNER':
        # Verificamos si ya creó el salón
        if hasattr(user, 'salon'):
            return render(request, 'dashboard/index.html', {'salon': user.salon})
        else:
            # Si es dueño pero no tiene salón, lo obligamos a crearlo
            return redirect('create_salon')

    # 2. CASO EMPLEADO
    if user.role == 'EMPLOYEE':
        return redirect('employee_settings')

    # 3. CASO CLIENTE (Por defecto)
    bookings = Booking.objects.filter(customer=user).order_by('-start_time')
    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def create_salon_view(request):
    """
    Solo para dueños que aún no tienen salón.
    """
    # Si ya tiene salón, lo sacamos de aquí
    if hasattr(request.user, 'salon'):
        return redirect('dashboard')

    if request.method == 'POST':
        form = SalonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                
                # Re-confirmamos que sea dueño
                request.user.role = 'OWNER'
                request.user.save()

            messages.success(request, "¡Negocio creado! Ahora configura tus servicios.")
            return redirect('manage_services')
    else:
        form = SalonCreateForm()
        
    return render(request, 'dashboard/create_salon.html', {'form': form})

# Vistas auxiliares
def accept_invite_view(request): return redirect('dashboard')
def employee_join_view(request): return redirect('dashboard')