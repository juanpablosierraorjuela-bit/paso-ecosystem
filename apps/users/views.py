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

# --- HELPER: VINCULAR EMPLEADO ---
def vincular_empleado(user, salon):
    """Función auxiliar para no repetir código"""
    try:
        # Verificar si ya es empleado de este salón
        if Employee.objects.filter(user=user, salon=salon).exists():
            return True
            
        # Crear perfil
        Employee.objects.create(
            user=user,
            salon=salon,
            name=f"{user.first_name} {user.last_name}" or user.username,
            phone=getattr(user, 'phone', '')
        )
        # Asegurar rol
        user.role = 'EMPLOYEE'
        user.save()
        return True
    except Exception as e:
        logger.error(f"Error vinculando empleado: {e}")
        return False

def home(request):
    try:
        salons = list(Salon.objects.all().order_by('-id'))
    except:
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    # 1. Recuperar Token
    invite_token = request.GET.get('invite') or request.POST.get('invite_token')
    inviting_salon = None
    
    if invite_token:
        try:
            uuid_obj = uuid.UUID(str(invite_token))
            inviting_salon = Salon.objects.filter(invite_token=uuid_obj).first()
        except:
            pass

    # 2. CASO USUARIO YA LOGUEADO (El "Bucle" corregido)
    if request.user.is_authenticated:
        if inviting_salon:
            # Si ya está logueado y trae invitación, lo vinculamos YA
            if vincular_empleado(request.user, inviting_salon):
                messages.success(request, f"¡Te has unido a {inviting_salon.name}!")
                return redirect('employee_settings')
        return redirect('dashboard')

    # 3. REGISTRO NUEVO
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    
                    if inviting_salon:
                        # Forzar rol empleado
                        user.role = 'EMPLOYEE'
                        user.save()
                        # Vincular inmediatamente
                        vincular_empleado(user, inviting_salon)
                        logger.info(f"✅ Nuevo empleado registrado: {user.username}")
                    else:
                        user.save()

                login(request, user)
                
                # Redirección inteligente
                if inviting_salon:
                    return redirect('employee_settings') # Directo al panel
                return redirect('dashboard')

            except Exception as e:
                logger.error(f"Error registro: {e}")
                messages.error(request, "Error en el sistema. Intenta de nuevo.")
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
        return redirect('employee_join') # Si no tiene perfil, va a unirse

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
    """
    VISTA DE RESCATE: Si el empleado quedó en el limbo, aquí puede ingresar el código manualmente.
    """
    if request.method == 'POST':
        invite_token = request.POST.get('invite_token')
        if invite_token:
            try:
                uuid_obj = uuid.UUID(str(invite_token))
                salon = Salon.objects.filter(invite_token=uuid_obj).first()
                if salon:
                    if vincular_empleado(request.user, salon):
                        messages.success(request, f"¡Conectado exitosamente con {salon.name}!")
                        return redirect('employee_settings')
                    else:
                        messages.error(request, "Error al vincular. Intenta de nuevo.")
                else:
                    messages.error(request, "Código de invitación no válido.")
            except:
                messages.error(request, "Formato de código inválido.")
                
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