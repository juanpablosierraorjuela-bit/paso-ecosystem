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
    REGISTRO DE INVITACIÓN:
    El token viaja del Link -> Formulario -> Base de Datos -> Panel.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # 1. RECUPERAR EL TOKEN (Ya sea del Link o del Formulario enviado)
    invite_token = request.POST.get('invite_token') or request.GET.get('invite')
    inviting_salon = None
    
    if invite_token:
        try:
            uuid_obj = uuid.UUID(str(invite_token))
            inviting_salon = Salon.objects.filter(invite_token=uuid_obj).first()
        except:
            pass # Si el token falla, cargamos normal

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    
                    if inviting_salon:
                        # --- ES UN EMPLEADO CON INVITACIÓN ---
                        user.role = 'EMPLOYEE'
                        user.save()
                        
                        # Crear el vínculo INMEDIATAMENTE
                        Employee.objects.create(
                            user=user,
                            salon=inviting_salon,
                            name=f"{user.first_name} {user.last_name}" or user.username,
                            phone=getattr(user, 'phone', '')
                        )
                        
                        # Login y salto directo al panel
                        login(request, user)
                        messages.success(request, f"¡Bienvenido al equipo de {inviting_salon.name}!")
                        return redirect('employee_settings') # <--- SALTO MÁGICO
                        
                    else:
                        # --- ES UN DUEÑO O CLIENTE ---
                        user.save()
                        login(request, user)
                        return redirect('dashboard')

            except Exception as e:
                logger.error(f"Error registro: {e}")
                messages.error(request, "Error en el sistema. Intenta de nuevo.")
    else:
        # Configuración inicial del formulario
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
    Controlador de Tráfico
    """
    user = request.user
    role = getattr(user, 'role', 'CUSTOMER') 

    # --- EMPLEADO ---
    if role == 'EMPLOYEE':
        # Si ya tiene perfil, va al panel. Si no, va a la pantalla de código.
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
    """Vista de respaldo por si el link falla"""
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