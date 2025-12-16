from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
import logging

# Logger para monitoreo en Render
logger = logging.getLogger(__name__)

from apps.businesses.models import Salon, Employee, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    """Página de inicio"""
    try:
        salons = list(Salon.objects.all().order_by('-id'))
    except Exception as e:
        logger.error(f"Error cargando Home: {e}")
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """Registro con redirección inteligente según el Rol"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Iniciar sesión automáticamente
            login(request, user)
            # El dashboard se encargará de redirigir según el rol elegido
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    CONTROLADOR DE TRÁFICO CENTRAL
    Redirige a cada usuario a su panel correspondiente según su ROL.
    """
    user = request.user

    # --- CASO 1: COLABORADOR / EMPLEADO ---
    if user.role == 'EMPLOYEE':
        try:
            # Verificamos si ya está vinculado a un salón (tiene perfil Employee)
            if hasattr(user, 'employee') and user.employee:
                return redirect('employee_settings') # Panel de Empleado (Horarios/Telegram)
            else:
                # Se registró como empleado pero aún no tiene jefe/salón
                return redirect('employee_join') # Pantalla de "Unirse a un Equipo"
        except Exception as e:
            logger.error(f"Error en dashboard empleado: {e}")
            return redirect('employee_join')

    # --- CASO 2: DUEÑO (ADMIN) ---
    if user.role == 'ADMIN' or getattr(user, 'is_business_owner', False):
        try:
            salon = Salon.objects.filter(owner=user).first()
            if not salon:
                return redirect('create_salon') # Debe crear su negocio
            return render(request, 'dashboard/index.html', {'salon': salon}) # Panel de Dueño
        except Exception as e:
            logger.error(f"Error en dashboard dueño: {e}")

    # --- CASO 3: CLIENTE (CUSTOMER) ---
    # Si es Customer o cualquier otro rol no definido, va al panel de cliente
    bookings = []
    try:
        bookings = list(Booking.objects.filter(customer=user).order_by('-start_time'))
    except Exception as e:
        logger.error(f"Error cargando reservas de cliente: {e}")
        bookings = []

    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def employee_join_view(request):
    """Vista para colaboradores nuevos que buscan unirse a un salón"""
    # Aquí podrías agregar lógica para buscar salón o ingresar un código
    # Por ahora renderizamos la plantilla estática que ya tienes
    return render(request, 'registration/employee_join.html')

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