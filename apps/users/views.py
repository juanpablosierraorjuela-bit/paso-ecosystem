from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

# --- IMPORTACIONES CORRECTAS ---
# Modelos de Negocio (desde apps.businesses)
from apps.businesses.models import Salon
from apps.businesses.forms import SalonCreateForm
# Formularios de Usuario (Registro)
from .forms import CustomUserCreationForm

def home(request):
    """Página de inicio: Muestra los salones disponibles"""
    salons = Salon.objects.all().order_by('-id')
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """Vista de Registro de Usuarios (Clientes y Dueños)"""
    # Si ya está logueado, lo mandamos al dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Iniciar sesión automáticamente tras el registro
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    Panel de Control Principal:
    - Dueños: Ven su salón o formulario para crearlo.
    - Empleados/Clientes: Ven su panel correspondiente.
    """
    user = request.user
    
    # Lógica para determinar si es dueño (ADMIN)
    is_owner = getattr(user, 'role', '') == 'ADMIN' or getattr(user, 'is_business_owner', False)

    if is_owner:
        salon = Salon.objects.filter(owner=user).first()
        if not salon:
            return redirect('create_salon')
        return render(request, 'dashboard/index.html', {'salon': salon})

    # Lógica para Empleados/Clientes
    return render(request, 'dashboard/employee_dashboard.html')

@login_required
def create_salon_view(request):
    """Formulario para que un dueño registre su negocio"""
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
    """Perfil público del salón"""
    salon = get_object_or_404(Salon, slug=slug)
    return render(request, 'salon_detail.html', {'salon': salon})