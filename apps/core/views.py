from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.businesses.forms import OwnerRegistrationForm
from apps.businesses.models import Salon
from apps.core.models import User, GlobalSettings
from apps.marketplace.models import Appointment
from apps.core.forms import ClientProfileForm, ClientPasswordForm
import re

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
            return redirect('dashboard')
    else:
        form = OwnerRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    pass

@login_required
def dispatch_user(request):
    user = request.user
    if user.role == 'OWNER':
        return redirect('dashboard')
    elif user.role == 'CLIENT':
        return redirect('marketplace_home')
    elif user.role == 'EMPLOYEE':
        return redirect('employee_dashboard')
    elif user.is_superuser:
        return redirect('/admin/')
    else:
        return redirect('home')

@login_required
def client_dashboard(request):
    user = request.user
    
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
    
    # CORRECCIÓN: Prefetch_related para cargar los servicios eficientemente
    appointments = Appointment.objects.filter(client=user).exclude(status='CANCELLED').order_by('-created_at').prefetch_related('services')
    
    for app in appointments:
        if app.status == 'PENDING':
            elapsed = timezone.now() - app.created_at
            remaining = timedelta(minutes=60) - elapsed
            app.seconds_left = max(0, int(remaining.total_seconds()))
            
            try:
                owner_phone = app.salon.owner.phone or '573000000000'
                clean_phone = re.sub(r'\D', '', str(owner_phone))
                if not clean_phone.startswith('57'): clean_phone = '57' + clean_phone
            except:
                clean_phone = '573000000000'
            
            # CORRECCIÓN: Listar todos los servicios en el mensaje de WhatsApp
            servicios_nombres = ", ".join([s.name for s in app.services.all()])
            
            msg = (
                f"Hola {app.salon.name}, soy {user.first_name}. "
                f"Confirmo mi cita para {servicios_nombres} el {app.date_time.strftime('%d/%m %I:%M %p')}. "
                f"Adjunto abono de ${int(app.deposit_amount)}."
            )
            app.wa_link = f"https://wa.me/{clean_phone}?text={msg.replace(' ', '%20')}"
            
    context = {
        'appointments': appointments,
        'profile_form': profile_form,
        'password_form': password_form
    }
    return render(request, 'core/client_dashboard.html', context)