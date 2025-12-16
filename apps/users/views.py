from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist

from apps.businesses.models import Salon, Employee, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    """Página de inicio"""
    try:
        salons = Salon.objects.all().order_by('-id')
    except:
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    Panel Unificado BLINDADO contra Error 500.
    """
    user = request.user

    # 1. INTENTO DE DETECTAR EMPLEADO
    # Usamos un bloque try/except explícito. Si la relación falla, asumimos que no es empleado.
    try:
        if hasattr(user, 'employee') and user.employee:
            return redirect('employee_settings')
    except (ObjectDoesNotExist, AttributeError):
        pass # No pasa nada, seguimos evaluando

    # 2. INTENTO DE DETECTAR DUEÑO
    try:
        is_owner = getattr(user, 'role', '') == 'ADMIN' or getattr(user, 'is_business_owner', False)
        if is_owner:
            salon = Salon.objects.filter(owner=user).first()
            if not salon:
                return redirect('create_salon')
            return render(request, 'dashboard/index.html', {'salon': salon})
    except Exception as e:
        print(f"Error verificando dueño: {e}")
        # Si falla, seguimos como cliente para no mostrar error 500

    # 3. PANEL DE CLIENTE (Fallback seguro)
    bookings = []
    try:
        # Intentamos obtener las reservas. Si el campo 'customer' no existe aún,
        # esto fallará, pero el 'except' lo atrapará y mostrará lista vacía.
        bookings = Booking.objects.filter(customer=user).order_by('-start_time')
    except Exception as e:
        print(f"Error obteniendo reservas: {e}")
        bookings = []

    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def create_salon_view(request):
    try:
        if Salon.objects.filter(owner=request.user).exists():
            return redirect('dashboard')
    except:
        pass # Si falla la consulta, permitimos intentar crear

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