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
    except:
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """
    PASO 1: REGISTRO
    Si hay invitación, la guardamos en la sesión y enviamos a la pantalla de aceptación.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Detectar token en URL
    invite_token = request.GET.get('invite')
    inviting_salon = None
    
    if invite_token:
        try:
            uuid_obj = uuid.UUID(str(invite_token))
            inviting_salon = Salon.objects.filter(invite_token=uuid_obj).first()
        except:
            pass

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Recuperar token del formulario si existe
            posted_token = request.POST.get('invite_token')
            
            # Guardar usuario
            if posted_token:
                user.role = 'EMPLOYEE' # Pre-asignamos rol si viene invitado
            user.save()
            
            # Iniciar sesión
            login(request, user)

            # --- LÓGICA DE INVITACIÓN ---
            if posted_token:
                # Guardamos el token en la "mochila" (sesión) del usuario
                request.session['pending_invite'] = posted_token
                return redirect('accept_invite') # VAMOS A LA NUEVA PÁGINA
            
            return redirect('dashboard')
    else:
        # Pre-seleccionar rol
        initial_data = {}
        if inviting_salon:
            initial_data = {'role': 'EMPLOYEE'}
        form = CustomUserCreationForm(initial=initial_data)

    return render(request, 'registration/register.html', {
        'form': form, 
        'inviting_salon': inviting_salon
    })

@login_required
def accept_invite_view(request):
    """
    PASO 2: PANTALLA INTERMEDIA DE ACEPTACIÓN
    """
    # Recuperar token de la sesión
    token = request.session.get('pending_invite')
    
    if not token:
        return redirect('dashboard') # Si no hay invitación, para la casa

    salon = None
    try:
        uuid_obj = uuid.UUID(str(token))
        salon = Salon.objects.filter(invite_token=uuid_obj).first()
    except:
        pass

    if not salon:
        return redirect('dashboard')

    if request.method == 'POST':
        # --- EL EMPLEADO DIJO "SI" ---
        try:
            # Crear perfil
            Employee.objects.get_or_create(
                user=request.user,
                salon=salon,
                defaults={
                    'name': f"{request.user.first_name} {request.user.last_name}" or request.user.username,
                    'phone': getattr(request.user, 'phone', '')
                }
            )
            # Asegurar rol
            request.user.role = 'EMPLOYEE'
            request.user.save()
            
            # Limpiar sesión
            if 'pending_invite' in request.session:
                del request.session['pending_invite']
                
            messages.success(request, f"¡Ahora eres parte de {salon.name}!")
            return redirect('employee_settings') # AL PANEL POR FIN
            
        except Exception as e:
            logger.error(f"Error aceptando invitación: {e}")
            messages.error(request, "Ocurrió un error al unirsite.")
            return redirect('dashboard')

    return render(request, 'registration/accept_invite.html', {'salon': salon})

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