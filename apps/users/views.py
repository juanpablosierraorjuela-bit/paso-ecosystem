from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
import logging

# Logger para ver errores en Render si algo falla
logger = logging.getLogger(__name__)

from apps.businesses.models import Salon, Employee, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    try:
        salons = list(Salon.objects.all().order_by('-id'))
    except:
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """
    Registro BLINDADO: Asegura que el empleado se cree SÍ o SÍ antes de redirigir.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # 1. Recuperar token de invitación (si existe)
    invite_token = request.GET.get('invite') or request.POST.get('invite_token')
    inviting_salon = None
    
    if invite_token:
        try:
            inviting_salon = Salon.objects.get(invite_token=invite_token)
            logger.info(f"--- INVITACIÓN DETECTADA PARA: {inviting_salon.name} ---")
        except Salon.DoesNotExist:
            logger.warning("--- TOKEN DE INVITACIÓN INVÁLIDO O NO ENCONTRADO ---")

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # --- LÓGICA CRÍTICA: CREACIÓN DEL EMPLEADO ---
            if inviting_salon:
                logger.info(f"--- REGISTRANDO EMPLEADO: {user.username} ---")
                
                # 1. Forzar el rol de empleado
                user.role = 'EMPLOYEE'
                user.save() 
                
                # 2. Crear el perfil Employee INMEDIATAMENTE
                try:
                    Employee.objects.create(
                        user=user,
                        salon=inviting_salon,
                        name=f"{user.first_name} {user.last_name}" or user.username,
                        phone=getattr(user, 'phone', '')
                    )
                    logger.info("--- OBJETO EMPLOYEE CREADO EXITOSAMENTE ---")
                except Exception as e:
                    logger.error(f"--- ERROR FATAL CREANDO EMPLOYEE: {e} ---")
            else:
                # Registro normal (Dueño o Cliente)
                user.save()

            # 3. Iniciar sesión y redirigir al Dashboard
            login(request, user)
            return redirect('dashboard')
    else:
        # Pre-configurar el formulario si hay invitación
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
    Enrutador Inteligente: Redirige según el ROL y el estado del usuario.
    """
    user = request.user
    role = getattr(user, 'role', 'CUSTOMER') 

    # --- ROL EMPLEADO ---
    if role == 'EMPLOYEE':
        # Verificación: ¿Tiene el perfil de empleado creado?
        if hasattr(user, 'employee'):
            return redirect('employee_settings') # ¡ÉXITO! Va al panel de horarios.
        else:
            # Si tiene el rol pero no el perfil, algo falló o no usó invitación.
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

    # --- ROL CLIENTE (Por defecto) ---
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