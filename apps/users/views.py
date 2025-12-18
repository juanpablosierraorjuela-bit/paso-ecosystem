from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages

# Importamos modelos necesarios
from apps.businesses.models import Salon, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    """Página de inicio pública"""
    salons = Salon.objects.all().order_by('-id')
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """
    Vista de Registro Inteligente.
    Guarda el usuario y lo redirige según el rol que eligió.
    """
    # Si ya está logueado, lo mandamos al dashboard para que el dashboard decida
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Iniciamos sesión automáticamente tras el registro
            login(request, user)
            
            # --- LÓGICA DE DIRECCIONAMIENTO ---
            if user.role == 'OWNER':
                # Si se registró como DUEÑO, lo mandamos a crear su salón
                return redirect('create_salon')
            
            elif user.role == 'EMPLOYEE':
                # Si es EMPLEADO, a su configuración
                return redirect('employee_settings')
            
            else:
                # Si es CLIENTE, al inicio
                return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    Panel de Control Central (Traffic Controller).
    Cada vez que alguien hace clic en "Panel" o "Mi Cuenta", pasa por aquí.
    """
    user = request.user

    # CASO 1: DUEÑO
    if user.role == 'OWNER':
        if hasattr(user, 'salon'):
            # Si ya tiene salón, mostramos su panel de métricas
            return render(request, 'dashboard/index.html', {'salon': user.salon})
        else:
            # Si es dueño pero NO tiene salón, lo obligamos a crearlo
            return redirect('create_salon')

    # CASO 2: EMPLEADO
    if user.role == 'EMPLOYEE':
        return redirect('employee_settings')

    # CASO 3: CLIENTE (Por defecto)
    # Mostramos sus citas futuras
    bookings = Booking.objects.filter(customer=user).order_by('-start_time')
    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def create_salon_view(request):
    """
    Vista para crear el negocio (Solo para Dueños nuevos)
    """
    # Si ya tiene salón, no debería estar aquí
    if hasattr(request.user, 'salon'):
        return redirect('dashboard')

    if request.method == 'POST':
        form = SalonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                
                # Reaseguramos que el rol sea OWNER
                request.user.role = 'OWNER'
                request.user.save()

            messages.success(request, "¡Negocio creado exitosamente!")
            # Al terminar, lo mandamos a agregar servicios
            return redirect('manage_services')
    else:
        form = SalonCreateForm()
        
    return render(request, 'dashboard/create_salon.html', {'form': form})

# Vistas de soporte (necesarias para evitar errores de importación)
def accept_invite_view(request):
    return redirect('dashboard')

def employee_join_view(request):
    return redirect('dashboard')