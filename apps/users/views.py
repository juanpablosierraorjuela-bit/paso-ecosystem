from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

# --- IMPORTACIONES CORRECTAS ---
from apps.businesses.models import Salon
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    """Página de inicio"""
    salons = Salon.objects.all().order_by('-id')
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """Vista de Registro de Usuarios"""
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
    """Panel de Control Principal"""
    user = request.user
    is_owner = getattr(user, 'role', '') == 'ADMIN' or getattr(user, 'is_business_owner', False)

    if is_owner:
        salon = Salon.objects.filter(owner=user).first()
        if not salon:
            return redirect('create_salon')
        return render(request, 'dashboard/index.html', {'salon': salon})

    return render(request, 'dashboard/employee_dashboard.html')

@login_required
def create_salon_view(request):
    """Crear Salón"""
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
    salon = get_object_or_404(Salon, slug=slug)
    return render(request, 'salon_detail.html', {'salon': salon})