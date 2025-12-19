from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages

# Importamos los modelos y formularios necesarios
from apps.businesses.models import Salon, Booking, Service
from apps.businesses.forms import SalonCreateForm, ServiceForm
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

    # 1. LOGICA PARA EL DUEÑO (Aquí estaba faltando el formulario)
    if hasattr(user, 'salon'):
        salon = user.salon
        
        # Inicializamos el formulario de servicios
        s_form = ServiceForm()
        
        # Procesamos si se está creando un servicio
        if request.method == 'POST' and 'create_service' in request.POST:
            s_form = ServiceForm(request.POST)
            if s_form.is_valid():
                service = s_form.save(commit=False)
                service.salon = salon
                service.save()
                messages.success(request, "¡Nuevo servicio agregado con éxito!")
                return redirect('dashboard')
            else:
                messages.error(request, "Error al crear el servicio. Revisa los campos.")

        # Obtenemos la lista de servicios para mostrar en la tabla
        services = salon.services.all()

        context = {
            'salon': salon,
            's_form': s_form,     # <--- ¡ESTO FALTABA!
            'services': services, # <--- Y ESTO TAMBIÉN
        }
        return render(request, 'dashboard/index.html', context)

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
        form = SalonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                
                request.user.role = 'OWNER'
                request.user.save()

            return redirect('dashboard')
    else:
        form = SalonCreateForm()
        
    return render(request, 'dashboard/create_salon.html', {'form': form})

# Views de compatibilidad
def accept_invite_view(request):
    return redirect('dashboard')

def employee_join_view(request):
    return redirect('dashboard')