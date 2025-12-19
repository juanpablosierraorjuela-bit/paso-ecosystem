from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages

# Modelos
from apps.businesses.models import Salon, Booking, Service
# Formularios (Asegúrate de que ServiceForm existe en forms.py)
from apps.businesses.forms import SalonForm, ServiceForm
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

    # 1. LÓGICA PARA EL DUEÑO (Aquí es donde estaba el fallo)
    if hasattr(user, 'salon'):
        salon = user.salon
        
        # A. PROCESAR FORMULARIO DE NUEVO SERVICIO (POST)
        if request.method == 'POST' and 'create_service' in request.POST:
            s_form = ServiceForm(request.POST)
            if s_form.is_valid():
                service = s_form.save(commit=False)
                service.salon = salon
                service.save()
                messages.success(request, '¡Servicio creado exitosamente!')
                return redirect('dashboard') # Recargar para limpiar datos
            else:
                messages.error(request, 'Error al crear servicio. Verifica los datos.')
        
        # B. PREPARAR DATOS PARA LA PANTALLA (GET)
        services = salon.services.all().order_by('name') # Lista de servicios
        s_form = ServiceForm() # Formulario vacío para el Modal

        context = {
            'salon': salon,
            'services': services, 
            's_form': s_form
        }
        return render(request, 'dashboard/index.html', context)

    # 2. LÓGICA PARA EL EMPLEADO
    if hasattr(user, 'employee'):
        return redirect('employee_settings')

    # 3. LÓGICA PARA EL CLIENTE
    bookings = Booking.objects.filter(customer=user).order_by('-start_time')
    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def create_salon_view(request):
    if hasattr(request.user, 'salon'):
        return redirect('dashboard')

    if request.method == 'POST':
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
        form = SalonForm()
        
    return render(request, 'dashboard/create_salon.html', {'form': form})

# Views obsoletas
def accept_invite_view(request):
    return redirect('dashboard')

def employee_join_view(request):
    return redirect('dashboard')