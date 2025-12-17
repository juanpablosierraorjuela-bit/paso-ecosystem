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

# --- FUNCIÓN AUXILIAR: VINCULAR Y SALTAR ---
def vincular_empleado_y_redirigir(request, user, salon):
    """Vincula al usuario con el salón y lo manda al panel de horarios"""
    try:
        # Verificar o crear el perfil de empleado
        employee, created = Employee.objects.get_or_create(
            user=user,
            salon=salon,
            defaults={
                'name': f"{user.first_name} {user.last_name}" or user.username,
                'phone': getattr(user, 'phone', '')
            }
        )
        
        # Asegurar el rol
        if user.role != 'EMPLOYEE':
            user.role = 'EMPLOYEE'
            user.save()

        # Mensaje de éxito y redirección
        messages.success(request, f"¡Bienvenido al equipo de {salon.name}!")
        return redirect('employee_settings')

    except Exception as e:
        logger.error(f"Error vinculando empleado: {e}")
        messages.error(request, "Error al procesar la invitación.")
        return redirect('dashboard')

def home(request):
    try:
        salons = list(Salon.objects.all().order_by('-id'))
    except:
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """
    REGISTRO INTELIGENTE: Maneja usuarios nuevos y existentes con invitación.
    """
    # 1. RECUPERAR TOKEN (Prioridad: POST > GET)
    invite_token = request.POST.get('invite_token') or request.GET.get('invite')
    inviting_salon = None
    
    # 2. VALIDAR TOKEN
    if invite_token:
        try:
            uuid_obj = uuid.UUID(str(invite_token))
            inviting_salon = Salon.objects.filter(invite_token=uuid_obj).first()
        except:
            pass # Token inválido, continuamos normal

    # 3. CASO: USUARIO YA LOGUEADO QUE CLIQUEA EL LINK
    if request.user.is_authenticated:
        if inviting_salon:
            # ¡Lo vinculamos de inmediato!
            return vincular_empleado_y_redirigir(request, request.user, inviting_salon)
        return redirect('dashboard')

    # 4. CASO: REGISTRO DE USUARIO NUEVO
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    
                    if inviting_salon:
                        # Guardar como empleado
                        user.role = 'EMPLOYEE'
                        user.save()
                        
                        # Iniciar sesión antes de redirigir
                        login(request, user)
                        
                        # VINCULAR Y SALTAR
                        return vincular_empleado_y_redirigir(request, user, inviting_salon)
                    else:
                        # Registro normal (Dueño/Cliente)
                        user.save()
                        login(request, user)
                        return redirect('dashboard')

            except Exception as e:
                logger.error(f"Error crítico registro: {e}")
                messages.error(request, "Error del sistema al crear cuenta.")
        else:
            # Si el formulario no es válido, mostramos errores en consola para depurar
            logger.warning(f"Errores de formulario: {form.errors}")
            messages.error(request, "Por favor corrige los errores en el formulario.")
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

    # --- ROL EMPLEADO ---
    if role == 'EMPLOYEE':
        if hasattr(user, 'employee'):
            return redirect('employee_settings')
        return redirect('employee_join')

    # --- ROL DUEÑO ---
    elif role in ['ADMIN', 'OWNER'] or getattr(user, 'is_business_owner', False):
        try:
            salon = Salon.objects.filter(owner=user).first()
            if not salon:
                return redirect('create_salon')
            return render(request, 'dashboard/index.html', {'salon': salon})
        except:
            return redirect('create_salon')

    # --- ROL CLIENTE ---
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
    Vista de respaldo: Si cayeron aquí, pueden pegar el código manual.
    """
    if request.method == 'POST':
        token = request.POST.get('invite_token')
        try:
            uuid_obj = uuid.UUID(str(token))
            salon = Salon.objects.filter(invite_token=uuid_obj).first()
            if salon:
                return vincular_empleado_y_redirigir(request, request.user, salon)
            else:
                messages.error(request, "Código no encontrado.")
        except:
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