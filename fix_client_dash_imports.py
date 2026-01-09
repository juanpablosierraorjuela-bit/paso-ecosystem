import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# CONTENIDO CORRECTO DE APPS/CORE/VIEWS.PY
# ==========================================
core_views_content = """
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
    # La vista de login la maneja Django auth, pero si necesitamos custom logic va aqui
    # Por ahora usamos la generica en urls.py, este es un placeholder si se necesita
    pass

# --- SEMÁFORO DE BIENVENIDA ---
@login_required
def dispatch_user(request):
    user = request.user
    
    # 1. Si es Dueño -> Panel de Negocio
    if user.role == 'OWNER':
        return redirect('dashboard')
    
    # 2. Si es Cliente -> Marketplace
    elif user.role == 'CLIENT':
        return redirect('marketplace_home')
        
    # 3. Si es Empleado -> Su Agenda
    elif user.role == 'EMPLOYEE':
        return redirect('employee_dashboard')
        
    # 4. Si eres TÚ (Superuser) -> Admin de Django
    elif user.is_superuser:
        return redirect('/admin/')
        
    else:
        return redirect('home')

# --- PANEL CLIENTE ---
@login_required
def client_dashboard(request):
    # Permitir a dueños y empleados ver su perfil de cliente tambien si quieren, 
    # o restringir solo a CLIENT. Por ahora restringimos a CLIENT para seguir la Biblia.
    # Pero si un dueño reserva, quizás quiera ver sus citas. 
    # Para no romper, dejamos que cualquiera logueado vea SUS citas.
    
    appointments = Appointment.objects.filter(client=request.user).order_by('-created_at')
    
    # Procesar lógica de WhatsApp para cada cita
    for app in appointments:
        if app.status == 'PENDING':
            # Calcular tiempo restante (60 min)
            elapsed = timezone.now() - app.created_at
            remaining = timedelta(minutes=60) - elapsed
            app.seconds_left = max(0, int(remaining.total_seconds()))
            
            # Link WhatsApp
            try:
                owner_phone = app.salon.owner.phone
                clean_phone = re.sub(r'\D', '', str(owner_phone)) if owner_phone else '573000000000'
            except:
                clean_phone = '573000000000'
            
            msg = (
                f"Hola {app.salon.name}, soy {request.user.first_name}. "
                f"Confirmo mi cita para {app.service.name} el {app.date_time.strftime('%d/%m %I:%M %p')}. "
                f"Adjunto abono de ${int(app.deposit_amount)}."
            )
            app.wa_link = f"https://wa.me/{clean_phone}?text={msg}"
            
    return render(request, 'core/client_dashboard.html', {'appointments': appointments})
"""

def fix_imports():
    print("🚑 ARREGLANDO IMPORTS EN CORE VIEWS...")
    file_path = BASE_DIR / 'apps' / 'core' / 'views.py'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(core_views_content.strip())
    print("✅ apps/core/views.py reescrito con timezone importado.")

if __name__ == "__main__":
    fix_imports()