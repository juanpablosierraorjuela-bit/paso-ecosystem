from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages

from apps.businesses.models import Salon, Booking
# CORRECCIÓN: Importamos SalonForm en lugar de SalonCreateForm
from apps.businesses.forms import SalonForm
from .forms import CustomUserCreationForm

def home(request):
    salons = Salon.objects.all().order_by('-id')
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """Registro solo para Clientes o Nuevos Dueños"""
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
    user = request.user

    # 1. DUEÑO
    if hasattr(user, 'salon'):
        return render(request, 'dashboard/index.html', {'salon': user.salon})

    # 2. EMPLEADO
    if hasattr(user, 'employee'):
        return redirect('employee_settings')

    # 3. CLIENTE
    bookings = Booking.objects.filter(customer=user).order_by('-start_time')
    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def create_salon_view(request):
    if hasattr(request.user, 'salon'):
        return redirect('dashboard')

    if request.method == 'POST':
        # CORRECCIÓN: Usamos SalonForm aquí
        form = SalonForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                
                request.user.role = 'OWNER'
                request.user.save()

            return redirect('dashboard')
    else:
        # CORRECCIÓN: Y aquí también
        form = SalonForm()
        
    return render(request, 'dashboard/create_salon.html', {'form': form})

# Views obsoletas
def accept_invite_view(request):
    return redirect('dashboard')

def employee_join_view(request):
    return redirect('dashboard')