from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

# Importamos los modelos necesarios
from apps.businesses.models import Salon, Employee, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    """Página de inicio: Muestra los salones"""
    salons = Salon.objects.all().order_by('-id')
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """Registro de usuarios"""
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
    Panel Unificado (A prueba de errores 500)
    """
    user = request.user

    # 1. ¿ES EMPLEADO? (Método Seguro: hasattr)
    # Esto evita el error 500 si el usuario NO es empleado
    if hasattr(user, 'employee'):
        return redirect('employee_settings')

    # 2. ¿ES DUEÑO? -> Panel de Dueño
    is_owner = getattr(user, 'role', '') == 'ADMIN' or getattr(user, 'is_business_owner', False)
    
    if is_owner:
        # Intentamos obtener el salón del usuario
        salon = Salon.objects.filter(owner=user).first()
        
        # Si es dueño pero NO ha creado el salón, lo mandamos a crearlo
        if not salon:
            return redirect('create_salon')
            
        # Si ya tiene salón, mostramos el panel de negocio
        return render(request, 'dashboard/index.html', {'salon': salon})

    # 3. ¿ES CLIENTE? -> Panel de Cliente
    # Si no es empleado ni dueño, es cliente. Mostramos sus reservas.
    # El filtro 'customer=user' requiere que la migración de Booking se haya aplicado.
    my_bookings = Booking.objects.filter(customer=user).order_by('-start_time')
    
    return render(request, 'dashboard/client_dashboard.html', {'bookings': my_bookings})

@login_required
def create_salon_view(request):
    """Vista para crear el negocio por primera vez"""
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
    """Redirección a la vista detallada en businesses"""
    from apps.businesses.views import salon_detail as business_salon_detail
    return business_salon_detail(request, slug)