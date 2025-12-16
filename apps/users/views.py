from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

from apps.businesses.models import Salon, Employee, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    try:
        # Usamos list() para forzar la consulta y detectar errores aquí
        salons = list(Salon.objects.all().order_by('-id'))
    except Exception as e:
        logger.error(f"Error Home: {e}")
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # 1. Detectar Invitación
    invite_token = request.GET.get('invite') or request.POST.get('invite_token')
    inviting_salon = None
    
    if invite_token:
        try:
            inviting_salon = Salon.objects.get(invite_token=invite_token)
        except Exception:
            pass # Token inválido, registro normal

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Si hay invitación, forzamos rol EMPLEADO y vinculamos
            if inviting_salon:
                user.role = 'EMPLOYEE'
                user.save()
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
    """Redirección estricta por rol"""
    user = request.user
    # Si no tiene rol, asumimos CUSTOMER
    role = getattr(user, 'role', 'CUSTOMER') 

    # --- ROL EMPLEADO ---
    if role == 'EMPLOYEE':
        try:
            if hasattr(user, 'employee') and user.employee:
                return redirect('employee_settings')
            return redirect('employee_join')
        except:
            return redirect('employee_join')

    # --- ROL DUEÑO (ADMIN/OWNER) ---
    elif role in ['ADMIN', 'OWNER'] or getattr(user, 'is_business_owner', False):
        try:
            salon = Salon.objects.filter(owner=user).first()
            if not salon:
                return redirect('create_salon')
            return render(request, 'dashboard/index.html', {'salon': salon})
        except:
            # Si falla la BD, enviar a crear para intentar recuperar
            return redirect('create_salon')

    # --- ROL CLIENTE (Default) ---
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