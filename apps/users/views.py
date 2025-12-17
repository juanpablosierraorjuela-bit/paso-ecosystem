import uuid
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from apps.businesses.models import Salon, Employee, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

logger = logging.getLogger(__name__)

def home(request):
    """Landing Page Pública"""
    # Usamos prefetch_related si el modelo Salon tuviera relaciones costosas, 
    # pero para un listado simple esto está bien.
    salons = Salon.objects.all().order_by('-id')
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """
    Registro unificado. Detecta invitaciones para asignar roles automáticamente.
    """
    invite_token = request.GET.get('invite') or request.POST.get('invite_token')
    
    # 1. Verificar si hay un salón invitando (para UX)
    inviting_salon = None
    if invite_token:
        try:
            uuid_obj = uuid.UUID(str(invite_token))
            inviting_salon = Salon.objects.filter(invite_token=uuid_obj).first()
        except (ValueError, TypeError):
            pass

    # 2. Si ya está logueado, redirigir a aceptar invitación o al dashboard
    if request.user.is_authenticated:
        if invite_token:
            return redirect(f"/accept-invite/?invite={invite_token}")
        return redirect('dashboard')

    # 3. Procesar Formulario de Registro
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                # Asignamos rol preliminar si viene con invitación
                if invite_token:
                    user.role = 'EMPLOYEE'
                user.save()
            
            # Auto-Login
            login(request, user)

            # Redirigir al flujo de aceptación si hay token
            if invite_token:
                return redirect(f"/accept-invite/?invite={invite_token}")
            
            return redirect('dashboard')
    else:
        # Pre-llenar rol si detectamos invitación
        initial_data = {'role': 'EMPLOYEE'} if inviting_salon else {}
        form = CustomUserCreationForm(initial=initial_data)

    return render(request, 'registration/register.html', {
        'form': form, 
        'inviting_salon': inviting_salon,
        'invite_token': invite_token # Pasar al template para el campo oculto
    })

@login_required
def accept_invite_view(request):
    """
    Gestión segura de la aceptación de invitaciones.
    Evita conflictos si el usuario ya es empleado en otro lugar.
    """
    token = request.GET.get('invite')
    if not token:
        return redirect('dashboard')

    # 1. Validar el Salón
    try:
        uuid_obj = uuid.UUID(str(token))
        salon = Salon.objects.get(invite_token=uuid_obj)
    except (ValueError, ObjectDoesNotExist):
        messages.error(request, "El enlace de invitación no es válido o ha expirado.")
        return redirect('dashboard')

    # 2. Validar Estado Actual del Usuario
    # Verificar si ya es empleado (User -> Employee es OneToOne)
    if hasattr(request.user, 'employee'):
        current_salon = request.user.employee.salon
        if current_salon.id == salon.id:
            messages.info(request, "Ya eres parte de este equipo.")
            return redirect('employee_settings')
        else:
            # CASO CRÍTICO: Ya trabaja en otro lado
            messages.warning(request, f"No puedes unirte a {salon.name} porque ya estás registrado como empleado en {current_salon.name}. Contacta a soporte si esto es un error.")
            return redirect('dashboard')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Crear perfil de empleado
                Employee.objects.create(
                    user=request.user,
                    salon=salon,
                    name=f"{request.user.first_name} {request.user.last_name}",
                    phone=getattr(request.user, 'phone', '')
                )
                
                # Actualizar Rol solo si no era Dueño/Admin
                if request.user.role not in ['ADMIN', 'OWNER']:
                    request.user.role = 'EMPLOYEE'
                    request.user.save()
            
            messages.success(request, f"¡Bienvenido al equipo de {salon.name}!")
            return redirect('employee_settings')

        except Exception as e:
            logger.error(f"Error uniendo empleado: {e}")
            messages.error(request, "Ocurrió un error al procesar tu ingreso. Intenta de nuevo.")
            return redirect('dashboard')

    return render(request, 'registration/accept_invite.html', {'salon': salon, 'token': token})

@login_required
def dashboard_view(request):
    """
    Router Inteligente del Dashboard.
    Determina a dónde enviar al usuario basado en sus relaciones reales en DB.
    """
    user = request.user

    # PRIORIDAD 1: ¿Es Dueño de un Salón?
    # Usamos hasattr porque es una relación OneToOne inversa
    if hasattr(user, 'salon'):
        return render(request, 'dashboard/index.html', {'salon': user.salon})

    # PRIORIDAD 2: ¿Es Empleado?
    if hasattr(user, 'employee'):
        # Si tiene perfil de empleado, ver si tiene configuraciones pendientes
        return redirect('employee_settings')

    # PRIORIDAD 3: Cliente / Usuario Normal
    # Mostramos sus reservas
    bookings = Booking.objects.filter(customer=user).select_related('salon', 'service', 'employee').order_by('-start_time')
    
    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def employee_join_view(request):
    """Vista informativa cuando un empleado entra sin invitación"""
    return render(request, 'registration/employee_join.html')

@login_required
def create_salon_view(request):
    # Seguridad: Si ya tiene salón, no dejar crear otro
    if hasattr(request.user, 'salon'):
        return redirect('dashboard')

    if request.method == 'POST':
        form = SalonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                
                # Actualizar rol del usuario a OWNER
                request.user.role = 'OWNER'
                request.user.save()

            messages.success(request, "¡Tu negocio ha sido creado exitosamente!")
            return redirect('dashboard')
    else:
        form = SalonCreateForm()
        
    return render(request, 'dashboard/create_salon.html', {'form': form})

# Proxy para mantener compatibilidad de URLs
def salon_detail(request, slug):
    from apps.businesses.views import salon_detail as business_salon_detail
    return business_salon_detail(request, slug)