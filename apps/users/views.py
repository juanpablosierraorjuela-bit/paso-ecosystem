import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

from apps.businesses.models import Salon, Employee, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

# --- HELPER: VINCULACIÓN SEGURA ---
def vincular_y_redirigir(request, user, salon):
    """Vincula al usuario como empleado y lo manda al panel"""
    try:
        # Verificar si ya existe el vínculo
        employee, created = Employee.objects.get_or_create(
            user=user,
            salon=salon,
            defaults={
                'name': f"{user.first_name} {user.last_name}" or user.username,
                'phone': getattr(user, 'phone', '')
            }
        )
        
        # Asegurar Rol
        if user.role != 'EMPLOYEE':
            user.role = 'EMPLOYEE'
            user.save()

        # Login si es necesario (para registros nuevos)
        if not request.user.is_authenticated:
            login(request, user)

        messages.success(request, f"¡Bienvenido a {salon.name}!")
        return redirect('employee_settings') # <--- SALTO DIRECTO AL PANEL

    except Exception as e:
        logger.error(f"Error vinculando: {e}")
        messages.error(request, "Error al unirse al equipo.")
        return redirect('dashboard')

def home(request):
    try:
        salons = list(Salon.objects.all().order_by('-id'))
    except:
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """
    REGISTRO CON INVITACIÓN FLUIDA
    """
    # 1. Recuperar Token (GET o POST)
    invite_token = request.POST.get('invite_token') or request.GET.get('invite')
    inviting_salon = None
    
    if invite_token:
        try:
            uuid_obj = uuid.UUID(str(invite_token))
            inviting_salon = Salon.objects.filter(invite_token=uuid_obj).first()
        except:
            pass

    # 2. CASO: USUARIO YA LOGUEADO (Clic en link estando conectado)
    if request.user.is_authenticated:
        if inviting_salon:
            return vincular_y_redirigir(request, request.user, inviting_salon)
        return redirect('dashboard')

    # 3. CASO: REGISTRO NUEVO
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.save() # Guardamos primero el usuario base
                    
                    if inviting_salon:
                        # Si hay invitación, vinculamos y nos vamos
                        return vincular_y_redirigir(request, user, inviting_salon)
                    
                    # Registro normal
                    login(request, user)
                    return redirect('dashboard')

            except Exception as e:
                logger.error(f"Error registro: {e}")
                messages.error(request, "Error en el registro. Intenta de nuevo.")
    else:
        initial_data = {}
        if inviting_salon:
            initial_data = {'role': 'EMPLOYEE'}
        form = CustomUserCreationForm(initial=initial_data)

    return render(request, 'registration/register.html', {
        'form': form, 
        'inviting_salon': inviting_salon
    })

@login_required
def dashboard_view(request):
    user = request.user
    role = getattr(user, 'role', 'CUSTOMER') 

    # --- EMPLEADO ---
    if role == 'EMPLOYEE':
        if hasattr(user, 'employee'):
            return redirect('employee_settings')
        return redirect('employee_join')

    # --- DUEÑO ---
    elif role in ['ADMIN', 'OWNER'] or getattr(user, 'is_business_owner', False):
        try:
            salon = Salon.objects.filter(owner=user).first()
            if not salon:
                return redirect('create_salon')
            return render(request, 'dashboard/index.html', {'salon': salon})
        except:
            return redirect('create_salon')

    # --- CLIENTE ---
    else:
        bookings = []
        try:
            bookings = list(Booking.objects.filter(customer=user).order_by('-start_time'))
        except:
            bookings = []
        return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def employee_join_view(request):
    """Vista de respaldo manual"""
    if request.method == 'POST':
        token = request.POST.get('invite_token')
        try:
            uuid_obj = uuid.UUID(str(token))
            salon = Salon.objects.filter(invite_token=uuid_obj).first()
            if salon:
                return vincular_y_redirigir(request, request.user, salon)
        except:
            pass
        messages.error(request, "Código inválido.")
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