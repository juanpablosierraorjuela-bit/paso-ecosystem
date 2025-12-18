from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages

from apps.businesses.models import Salon, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    salons = Salon.objects.all().order_by('-id')
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """REGISTRO BLINDADO: Redirige OBLIGATORIAMENTE según el rol."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # 1. Guardamos el usuario sin commit para asignar rol manualmente si hace falta
            user = form.save(commit=False)
            
            # 2. Aseguramos que el rol venga del formulario
            role_selected = form.cleaned_data.get('role')
            if role_selected:
                user.role = role_selected
            
            user.save() # Guardamos definitivamente

            # 3. Iniciar sesión de inmediato
            login(request, user)
            
            # 4. CEREBRO DE DIRECCIONAMIENTO
            if user.role == 'OWNER':
                # ¡AQUÍ ESTÁ LA MAGIA! Si es dueño, va directo a crear salón
                return redirect('create_salon')
            
            elif user.role == 'EMPLOYEE':
                return redirect('employee_settings')
            
            else:
                return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    user = request.user

    # CASO DUEÑO
    if user.role == 'OWNER':
        if hasattr(user, 'salon'):
            return render(request, 'dashboard/index.html', {'salon': user.salon})
        else:
            return redirect('create_salon') # Si entra al panel sin salón, lo mandamos a crearlo

    # CASO EMPLEADO
    if user.role == 'EMPLOYEE':
        return redirect('employee_settings')

    # CASO CLIENTE
    bookings = Booking.objects.filter(customer=user).order_by('-start_time')
    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def create_salon_view(request):
    if hasattr(request.user, 'salon'):
        return redirect('dashboard')

    if request.method == 'POST':
        form = SalonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                
                request.user.role = 'OWNER'
                request.user.save()

            messages.success(request, "¡Bienvenido! Configura tus servicios.")
            return redirect('manage_services')
    else:
        form = SalonCreateForm()
        
    return render(request, 'dashboard/create_salon.html', {'form': form})

# Vistas de soporte
def accept_invite_view(request): return redirect('dashboard')
def employee_join_view(request): return redirect('dashboard')