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

def home(request):
    try:
        salons = list(Salon.objects.all().order_by('-id'))
    except Exception as e:
        logger.error(f"Error Home: {e}")
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """
    Registro BLINDADO contra errores 500.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # 1. Recuperar y Validar Token
    invite_token = request.GET.get('invite') or request.POST.get('invite_token')
    inviting_salon = None
    
    if invite_token:
        try:
            # Validamos que sea un UUID real antes de consultar la BD
            uuid_obj = uuid.UUID(str(invite_token))
            inviting_salon = Salon.objects.filter(invite_token=uuid_obj).first()
            if inviting_salon:
                logger.info(f"--- INVITACIÓN VÁLIDA: {inviting_salon.name} ---")
        except (ValueError, Exception) as e:
            logger.warning(f"--- TOKEN INVÁLIDO O ERROR: {e} ---")
            # No hacemos nada, simplemente cargamos el registro normal

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Transacción Atómica: O se crea todo o no se crea nada
                with transaction.atomic():
                    user = form.save(commit=False)
                    
                    if inviting_salon:
                        # Forzamos rol empleado
                        user.role = 'EMPLOYEE'
                        user.save()
                        
                        # Crear perfil Employee
                        Employee.objects.create(
                            user=user,
                            salon=inviting_salon,
                            name=f"{user.first_name} {user.last_name}" or user.username,
                            phone=getattr(user, 'phone', '')
                        )
                        logger.info(f"--- EMPLEADO CREADO: {user.username} ---")
                    else:
                        # Registro normal
                        user.save()

                # Login y Redirección
                login(request, user)
                messages.success(request, "¡Cuenta creada exitosamente!")
                return redirect('dashboard')

            except Exception as e:
                logger.error(f"Error crítico en registro: {e}")
                messages.error(request, "Hubo un error creando tu cuenta. Intenta de nuevo.")
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
    """
    Dashboard Robusto con Redirección Segura
    """
    user = request.user
    role = getattr(user, 'role', 'CUSTOMER')

    # --- ROL EMPLEADO ---
    if role == 'EMPLOYEE':
        # Verificamos la relación de forma segura
        if hasattr(user, 'employee') and user.employee:
            return redirect('employee_settings')
        else:
            # Si es empleado pero no tiene perfil, lo mandamos a unirse
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