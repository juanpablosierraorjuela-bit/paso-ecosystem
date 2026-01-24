from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import re

# Importes de tus apps
from apps.businesses.forms import OwnerRegistrationForm
from apps.businesses.models import Salon
from apps.core.models import User, GlobalSettings
from apps.marketplace.models import Appointment
from apps.core.forms import ClientProfileForm, ClientPasswordForm

def home(request):
    return render(request, 'home.html')

def landing_owners(request):
    return render(request, 'landing_owners.html')

def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido {user.first_name}! Tu salón ha sido registrado.")
            return redirect('dashboard')
    else:
        form = OwnerRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

@login_required
def dispatch_user(request):
    """Redirige al usuario según su rol después del login."""
    user = request.user
    if user.role == 'OWNER':
        return redirect('dashboard')
    elif user.role == 'CLIENT':
        return redirect('client_dashboard')
    elif user.role == 'EMPLOYEE':
        return redirect('employee_dashboard')
    elif user.is_superuser:
        return redirect('/control-maestro-seguro/')
    return redirect('home')

@login_required
def client_dashboard(request):
    user = request.user
    
    # Manejo de actualizaciones de perfil y contraseña
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ClientProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Tus datos han sido actualizados.")
                return redirect('client_dashboard')
        
        elif 'change_password' in request.POST:
            password_form = ClientPasswordForm(request.POST)
            if password_form.is_valid():
                new_pass = password_form.cleaned_data['new_password']
                user.set_password(new_pass)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada correctamente.")
                return redirect('client_dashboard')
    
    profile_form = ClientProfileForm(instance=user)
    password_form = ClientPasswordForm()
    
    # Citas del cliente (excluyendo canceladas)
    appointments = Appointment.objects.filter(
        client=user
    ).exclude(status='CANCELLED').order_by('-date_time').prefetch_related('services', 'salon')
    
    # Lógica de WhatsApp para citas PENDIENTES
    for app in appointments:
        if app.status == 'PENDING':
            try:
                # Obtenemos el teléfono del dueño del salón
                owner_phone = app.salon.owner.phone or '573000000000'
                clean_phone = re.sub(r'\D', '', str(owner_phone))
                if not clean_phone.startswith('57'): 
                    clean_phone = '57' + clean_phone
            except:
                clean_phone = '573000000000'
            
            servicios_nombres = ", ".join([s.name for s in app.services.all()])
            
            msg = (
                f"Hola {app.salon.name}, soy {user.first_name}. "
                f"Confirmo mi cita para {servicios_nombres} el {app.date_time.strftime('%d/%m %I:%M %p')}. "
                f"Adjunto abono de ${int(app.deposit_amount)}."
            )
            # Usamos quote para asegurar que el link sea válido
            import urllib.parse
            app.wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(msg)}"
            
    context = {
        'appointments': appointments,
        'profile_form': profile_form,
        'password_form': password_form
    }
    return render(request, 'core/client_dashboard.html', context)

@login_required
def employee_dashboard(request):
    user = request.user
    today = timezone.now().date()
    
    # IMPORTANTE: En tu models.py el estado es 'VERIFIED', no 'CONFIRMED'
    appointments = Appointment.objects.filter(
        employee=user, 
        status='VERIFIED', 
        date_time__date__gte=today
    ).order_by('date_time').prefetch_related('services', 'client')

    # Cálculo de saldo pendiente
    for app in appointments:
        total = app.total_price or 0
        deposit = app.deposit_amount or 0
        app.balance_due = total - deposit

    return render(request, 'core/employee_dashboard.html', {
        'appointments': appointments,
        'user': user
    })