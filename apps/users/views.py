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
        # Usamos list() para evitar errores de lazy loading
        salons = list(Salon.objects.all().order_by('-id'))
    except Exception as e:
        logger.error(f"Error cargando Home: {e}")
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """Registro de usuarios con inicio de sesión automático"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # El dashboard leerá el rol recién creado y redirigirá correctamente
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    CONTROLADOR DE TRÁFICO ESTRICTO
    Redirige a cada usuario a su panel correspondiente según su ROL.
    """
    user = request.user
    role = getattr(user, 'role', 'CUSTOMER') # Por defecto Cliente si no tiene rol

    # --- CASO 1: EMPLEADO (EMPLOYEE) ---
    if role == 'EMPLOYEE':
        try:
            # Verificamos si ya está vinculado a un salón
            if hasattr(user, 'employee') and user.employee:
                return redirect('employee_settings') # Panel de Gestión
            else:
                return redirect('employee_join') # Pantalla "Únete a un equipo"
        except Exception as e:
            logger.error(f"Error Dashboard Empleado: {e}")
            return redirect('employee_join')

    # --- CASO 2: DUEÑO (ADMIN) ---
    elif role == 'ADMIN' or getattr(user, 'is_business_owner', False):
        try:
            salon = Salon.objects.filter(owner=user).first()
            if not salon:
                return redirect('create_salon') # Debe crear su negocio primero
            return render(request, 'dashboard/index.html', {'salon': salon})
        except Exception as e:
            logger.error(f"Error Dashboard Dueño: {e}")
            # Si falla la BD, lo enviamos a crear salón para intentar arreglarlo
            return redirect('create_salon')

    # --- CASO 3: CLIENTE (CUSTOMER) - Solo si no es lo anterior ---
    else:
        bookings = []
        try:
            bookings = list(Booking.objects.filter(customer=user).order_by('-start_time'))
        except Exception as e:
            logger.error(f"Error Dashboard Cliente: {e}")
            bookings = []
        
        return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def employee_join_view(request):
    """Vista para colaboradores nuevos"""
    return render(request, 'registration/employee_join.html')

@login_required
def create_salon_view(request):
    """Vista para crear negocio"""
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