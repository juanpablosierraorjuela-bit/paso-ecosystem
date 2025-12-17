import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages
from django.urls import reverse
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
    """REGISTRO ROBUSTO (NO PIERDE EL TOKEN)"""
    # 1. Recuperar token (GET o POST)
    invite_token = request.GET.get('invite') or request.POST.get('invite_token')
    
    # Validar salón para mostrar nombre en pantalla
    inviting_salon = None
    if invite_token:
        try:
            uuid_obj = uuid.UUID(str(invite_token))
            inviting_salon = Salon.objects.filter(invite_token=uuid_obj).first()
        except:
            pass

    # 2. SI YA ESTÁ LOGUEADO -> Ir directo a aceptar
    if request.user.is_authenticated:
        if invite_token:
            return redirect(f"/accept-invite/?invite={invite_token}")
        return redirect('dashboard')

    # 3. PROCESAR REGISTRO
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Si hay invitación, preparamos rol
            if invite_token:
                user.role = 'EMPLOYEE'
                
            user.save()
            login(request, user)

            # --- REDIRECCIÓN SEGURA ---
            if invite_token:
                # Enviamos el token en la URL para que no se pierda
                return redirect(f"/accept-invite/?invite={invite_token}")
            
            return redirect('dashboard')
    else:
        initial = {'role': 'EMPLOYEE'} if inviting_salon else {}
        form = CustomUserCreationForm(initial=initial)

    return render(request, 'registration/register.html', {
        'form': form, 
        'inviting_salon': inviting_salon
    })

@login_required
def accept_invite_view(request):
    """VISTA INTERMEDIA: ¡HOLA, ÚNETE!"""
    # Intentamos recuperar el token de la URL (más seguro) o de la sesión
    token = request.GET.get('invite') or request.session.get('pending_invite')
    
    if not token:
        return redirect('dashboard')

    salon = None
    try:
        uuid_obj = uuid.UUID(str(token))
        salon = Salon.objects.filter(invite_token=uuid_obj).first()
    except:
        pass

    if not salon:
        messages.error(request, "La invitación no es válida.")
        return redirect('dashboard')

    if request.method == 'POST':
        # --- USUARIO DICE QUE SÍ ---
        try:
            Employee.objects.get_or_create(
                user=request.user,
                salon=salon,
                defaults={
                    'name': f"{request.user.first_name} {request.user.last_name}",
                    'phone': getattr(request.user, 'phone', '')
                }
            )
            request.user.role = 'EMPLOYEE'
            request.user.save()
            
            messages.success(request, f"¡Bienvenido a {salon.name}!")
            return redirect('employee_settings') # ---> AL PANEL
            
        except Exception as e:
            logger.error(f"Error uniendo: {e}")
            messages.error(request, "Error al unirse.")
            return redirect('dashboard')

    return render(request, 'registration/accept_invite.html', {'salon': salon, 'token': token})

@login_required
def dashboard_view(request):
    user = request.user
    role = getattr(user, 'role', 'CUSTOMER') 

    if role == 'EMPLOYEE':
        if hasattr(user, 'employee'):
            return redirect('employee_settings')
        return redirect('employee_join')

    elif role in ['ADMIN', 'OWNER'] or getattr(user, 'is_business_owner', False):
        try:
            salon = Salon.objects.filter(owner=user).first()
            if not salon:
                return redirect('create_salon')
            return render(request, 'dashboard/index.html', {'salon': salon})
        except:
            return redirect('create_salon')

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