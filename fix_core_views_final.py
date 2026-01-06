import os

# ==============================================================================
# CORE VIEWS (CORREGIDO)
# ==============================================================================
core_views_content = """
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required  # <--- ESTO FALTABA
from django.contrib.auth.views import LoginView
from apps.businesses.forms import OwnerRegistrationForm
from apps.marketplace.models import Appointment

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.user.is_authenticated:
        return redirect('businesses:dashboard')
        
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login
            return redirect('businesses:dashboard')
    else:
        form = OwnerRegistrationForm()
        
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    return LoginView.as_view(template_name='registration/login.html')(request)

# --- PANELES FALTANTES ---

@login_required
def client_dashboard(request):
    if request.user.role != 'CLIENT': return redirect('home')
    appointments = Appointment.objects.filter(client=request.user).order_by('-date_time')
    return render(request, 'core/client_dashboard.html', {'appointments': appointments})

@login_required
def employee_dashboard(request):
    if request.user.role != 'EMPLOYEE': return redirect('home')
    # Empleado ve sus citas asignadas y verificadas
    appointments = Appointment.objects.filter(employee=request.user, status='VERIFIED').order_by('date_time')
    return render(request, 'businesses/employee_dashboard.html', {'appointments': appointments})
"""

def main():
    path = 'apps/core/views.py'
    print(f"🚑 CORRIGIENDO {path} (Agregando importaciones faltantes)...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(core_views_content)
        print("✅ Archivo core/views.py reparado.")
        
        print("\n👉 EJECUTA AHORA:")
        print("python manage.py makemigrations")
        print("python manage.py migrate")
        print("git add .")
        print("git commit -m 'Fix: Add missing login_required import'")
        print("git push origin main")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()