from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
import logging

# Configurar logger para ver errores en Render
logger = logging.getLogger(__name__)

from apps.businesses.models import Salon, Employee, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    """Página de inicio"""
    try:
        # Usamos list() para forzar la consulta y evitar errores en el template
        salons = list(Salon.objects.all().order_by('-id'))
    except Exception as e:
        logger.error(f"Error cargando Home: {e}")
        salons = []
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
    Panel Unificado BLINDADO.
    Usa list() para capturar errores de BD antes de renderizar.
    """
    user = request.user

    # 1. INTENTO DE DETECTAR EMPLEADO
    try:
        # Forzamos la evaluación de la relación inversa
        if hasattr(user, 'employee') and user.employee:
            return redirect('employee_settings')
    except Exception as e:
        logger.warning(f"Usuario {user.id} no es empleado o falló la consulta: {e}")

    # 2. INTENTO DE DETECTAR DUEÑO
    try:
        is_owner = getattr(user, 'role', '') == 'ADMIN' or getattr(user, 'is_business_owner', False)
        if is_owner:
            salon = Salon.objects.filter(owner=user).first()
            if not salon:
                return redirect('create_salon')
            return render(request, 'dashboard/index.html', {'salon': salon})
    except Exception as e:
        logger.error(f"Error verificando dueño para {user.id}: {e}")
        # Si falla, seguimos para intentar mostrar panel de cliente

    # 3. PANEL DE CLIENTE (Fallback seguro)
    bookings = []
    try:
        # CRÍTICO: Usamos list() para que si la tabla Booking está rota, falle AQUI y no en el HTML
        bookings = list(Booking.objects.filter(customer=user).order_by('-start_time'))
    except Exception as e:
        logger.error(f"Error crítico obteniendo reservas (posible error de migración): {e}")
        bookings = [] # Mostramos lista vacía para no romper la página

    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def create_salon_view(request):
    try:
        if Salon.objects.filter(owner=request.user).exists():
            return redirect('dashboard')
    except:
        pass 

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