from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
import logging

# Logger para depuración (Mira esto en los logs de Render si algo falla)
logger = logging.getLogger(__name__)

from apps.businesses.models import Salon, Employee, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    try:
        salons = list(Salon.objects.all().order_by('-id'))
    except Exception as e:
        logger.error(f"Error cargando Home: {e}")
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """Registro con soporte para invitaciones"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    invite_token = request.GET.get('invite') or request.POST.get('invite_token')
    inviting_salon = None
    
    if invite_token:
        try:
            inviting_salon = Salon.objects.get(invite_token=invite_token)
        except:
            pass

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # LÓGICA DE ROLES EN REGISTRO
            if inviting_salon:
                user.role = 'EMPLOYEE'
                user.save()
                Employee.objects.create(
                    user=user, salon=inviting_salon, 
                    name=f"{user.first_name} {user.last_name}", phone=user.phone
                )
            else:
                # Guardamos el rol seleccionado en el formulario
                user.save()

            login(request, user)
            return redirect('dashboard')
    else:
        initial_data = {}
        if inviting_salon: initial_data = {'role': 'EMPLOYEE'}
        form = CustomUserCreationForm(initial=initial_data)

    return render(request, 'registration/register.html', {
        'form': form, 'inviting_salon': inviting_salon
    })

@login_required
def dashboard_view(request):
    """
    DASHBOARD UNIFICADO E INTELIGENTE
    """
    user = request.user
    role = getattr(user, 'role', 'CUSTOMER')
    
    # CHIVATO: Esto imprimirá en los logs de Render qué rol tiene el usuario
    logger.info(f"Usuario: {user.username} | Rol detectado: {role}")

    # --- ROL DE EMPLEADO ---
    if role == 'EMPLOYEE':
        try:
            if hasattr(user, 'employee') and user.employee:
                return redirect('employee_settings')
            else:
                return redirect('employee_join')
        except:
            return redirect('employee_join')

    # --- ROL DE DUEÑO (Soporta 'ADMIN' y 'OWNER') ---
    elif role in ['ADMIN', 'OWNER'] or getattr(user, 'is_business_owner', False):
        try:
            salon = Salon.objects.filter(owner=user).first()
            if not salon:
                return redirect('create_salon')
            return render(request, 'dashboard/index.html', {'salon': salon})
        except:
            return redirect('create_salon')

    # --- ROL DE CLIENTE (Por defecto) ---
    else:
        bookings = []
        try:
            bookings = list(Booking.objects.filter(customer=user).order_by('-start_time'))
        except:
            bookings = []
        return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def employee_join_view(request):
    return render(request, 'registration/employee_join.html')

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