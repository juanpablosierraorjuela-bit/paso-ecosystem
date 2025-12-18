from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages

# Importaciones clave (Asegúrate de que estas rutas existan)
from apps.businesses.models import Salon, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    """Página de inicio pública"""
    salons = Salon.objects.all().order_by('-id')
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """
    Registro Inteligente: Guarda el usuario y lo manda a su destino.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                
                # --- CEREBRO DE DIRECCIONAMIENTO ---
                if user.role == 'OWNER':
                    return redirect('create_salon')
                elif user.role == 'EMPLOYEE':
                    return redirect('employee_settings')
                else:
                    return redirect('home')
            except Exception as e:
                # Si falla algo interno, mostramos error en vez de pantalla blanca
                messages.error(request, f"Error en el registro: {e}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    Panel Central: Distribuye tráfico según quién seas.
    """
    user = request.user

    # 1. DUEÑO
    if user.role == 'OWNER':
        if hasattr(user, 'salon'):
            return render(request, 'dashboard/index.html', {'salon': user.salon})
        else:
            return redirect('create_salon')

    # 2. EMPLEADO
    if user.role == 'EMPLOYEE':
        return redirect('employee_settings')

    # 3. CLIENTE
    bookings = Booking.objects.filter(customer=user).order_by('-start_time')
    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def create_salon_view(request):
    """
    Paso obligatorio para dueños nuevos: Crear su local.
    """
    if hasattr(request.user, 'salon'):
        return redirect('dashboard')

    if request.method == 'POST':
        form = SalonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    salon = form.save(commit=False)
                    salon.owner = request.user
                    salon.save()
                    
                    # Aseguramos el rol
                    request.user.role = 'OWNER'
                    request.user.save()

                messages.success(request, "¡Negocio creado! Ahora configura tus servicios.")
                return redirect('manage_services')
            except Exception as e:
                messages.error(request, f"Error al guardar: {e}")
    else:
        form = SalonCreateForm()
        
    return render(request, 'dashboard/create_salon.html', {'form': form})

# Vistas auxiliares para evitar errores 404
def accept_invite_view(request): return redirect('dashboard')
def employee_join_view(request): return redirect('dashboard')