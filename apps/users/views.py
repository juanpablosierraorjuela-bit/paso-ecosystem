from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
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
    """Registro inteligente con soporte para invitaciones"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # 1. Detectar si hay invitación
    invite_token = request.GET.get('invite') or request.POST.get('invite_token')
    inviting_salon = None
    
    if invite_token:
        try:
            inviting_salon = Salon.objects.get(invite_token=invite_token)
        except:
            pass # Token inválido, registro normal

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # LÓGICA DE VINCULACIÓN AUTOMÁTICA
            if inviting_salon:
                user.role = 'EMPLOYEE' # Forzamos el rol
                user.save()
                # Creamos el perfil de empleado vinculado al salón
                Employee.objects.create(
                    user=user,
                    salon=inviting_salon,
                    name=f"{user.first_name} {user.last_name}",
                    phone=user.phone
                )
            else:
                user.save()

            login(request, user)
            return redirect('dashboard')
    else:
        # Pre-seleccionar rol si hay invitación
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
    """Enrutador de Paneles"""
    user = request.user
    role = getattr(user, 'role', 'CUSTOMER') 

    # Panel Empleado
    if role == 'EMPLOYEE':
        try:
            if hasattr(user, 'employee') and user.employee:
                return redirect('employee_settings')
            return redirect('employee_join')
        except:
            return redirect('employee_join')

    # Panel Dueño
    elif role in ['ADMIN', 'OWNER'] or getattr(user, 'is_business_owner', False):
        try:
            salon = Salon.objects.filter(owner=user).first()
            if not salon:
                return redirect('create_salon')
            return render(request, 'dashboard/index.html', {'salon': salon})
        except:
            return redirect('create_salon')

    # Panel Cliente
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