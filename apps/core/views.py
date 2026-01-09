from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from apps.businesses.forms import OwnerRegistrationForm
from apps.businesses.models import Salon
from apps.core.models import User, GlobalSettings
from apps.marketplace.models import Appointment
import re

def home(request):
    return render(request, 'home.html')

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
    appointments = Appointment.objects.filter(client=request.user).order_by('-created_at')
    
    for app in appointments:
        if app.status == 'PENDING':
            elapsed = timezone.now() - app.created_at
            remaining = timedelta(minutes=60) - elapsed
            app.seconds_left = max(0, int(remaining.total_seconds()))
            
            # --- CORRECCIÓN WHATSAPP COLOMBIA ---
            try:
                owner_phone = app.salon.owner.phone
                if owner_phone:
                    # Limpiar todo lo que no sea número
                    clean_phone = re.sub(r'\D', '', str(owner_phone))
                    # Si no empieza por 57, se lo pegamos
                    if not clean_phone.startswith('57'):
                        clean_phone = '57' + clean_phone
                else:
                    clean_phone = '573000000000'
            except:
                clean_phone = '573000000000'
            
            msg = (
                f"Hola {app.salon.name}, soy {request.user.first_name}. "
                f"Confirmo mi cita para {app.service.name} el {app.date_time.strftime('%d/%m %I:%M %p')}. "
                f"Adjunto abono de ${int(app.deposit_amount)}."
            )
            app.wa_link = f"https://wa.me/{clean_phone}?text={msg}"
            
    return render(request, 'core/client_dashboard.html', {'appointments': appointments})