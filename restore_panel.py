import os
import django
import sys

# Configurar Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.businesses.models import BusinessProfile, OperatingHour

# ==========================================
# 1. CIRUGÍA: RECUPERAR TU PANEL
# ==========================================
def fix_missing_profiles():
    User = get_user_model()
    # Buscamos a TODOS los dueños que estén "huérfanos" (sin negocio)
    owners = User.objects.filter(role='OWNER')
    
    print("🔍 Escaneando usuarios huérfanos...")
    count = 0
    
    for user in owners:
        if not hasattr(user, 'business_profile'):
            print(f"   🚑 Reparando usuario: {user.email}...")
            # Crear Perfil de Negocio
            profile = BusinessProfile.objects.create(
                owner=user,
                business_name=f"Negocio de {user.first_name}",
                address="Dirección por configurar",
                description="¡Bienvenido a tu Ecosistema!",
                deposit_percentage=30
            )
            # Crear Horarios Default
            for day_code, _ in OperatingHour.DAYS:
                OperatingHour.objects.create(
                    business=profile,
                    day_of_week=day_code,
                    opening_time="09:00",
                    closing_time="18:00",
                    is_closed=(day_code == 6)
                )
            count += 1
            
    if count > 0:
        print(f"✅ ¡ÉXITO! Se recuperaron {count} paneles de dueño.")
        print("👉 Intenta entrar a 'Mi Panel' ahora. Debería funcionar.")
    else:
        print("🎉 Todos los dueños tienen sus negocios en orden.")

# ==========================================
# 2. VACUNA: CORREGIR EL REGISTRO (APPS/CORE/VIEWS.PY)
# ==========================================
# Reescribimos la vista para asegurar que SIEMPRE cree el negocio
core_views_fixed = """from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from .forms import OwnerRegistrationForm
from django.urls import reverse_lazy
from .models import User
from apps.businesses.models import BusinessProfile, OperatingHour

# --- LANDING DE DOLORES ---
def pain_landing(request):
    return render(request, 'landing/pain_points.html')

# --- REGISTRO CORREGIDO ---
class OwnerRegisterView(CreateView):
    model = User
    form_class = OwnerRegistrationForm
    template_name = 'registration/register_owner.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # 1. Guardar Usuario
        user = form.save(commit=False)
        user.role = User.Role.OWNER
        user.save()
        
        # 2. GARANTÍA: Crear Perfil de Negocio Inmediatamente
        if not hasattr(user, 'business_profile'):
            # Intentamos tomar datos del formulario si existen, sino defaults
            biz_name = form.cleaned_data.get('business_name', f"Negocio de {user.first_name}")
            address = form.cleaned_data.get('address', "Dirección pendiente")
            
            profile = BusinessProfile.objects.create(
                owner=user,
                business_name=biz_name,
                address=address
            )
            
            # 3. Crear Horarios Default (Para que la agenda no falle)
            for day_code, _ in OperatingHour.DAYS:
                OperatingHour.objects.create(
                    business=profile,
                    day_of_week=day_code,
                    opening_time="09:00",
                    closing_time="19:00",
                    is_closed=(day_code == 6)
                )
                
        return super().form_valid(form)

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard_redirect(request):
    user = request.user
    if user.role == User.Role.OWNER:
        return redirect('businesses:dashboard')
    elif user.role == User.Role.EMPLOYEE:
        return redirect('booking:employee_dashboard')
    elif user.role == User.Role.CLIENT:
        return redirect('booking:client_dashboard')
    elif user.is_staff:
        return redirect('/admin/')
    return redirect('home')
"""

def apply_code_fix():
    print("🛠️ Aplicando parche de seguridad al código de registro...")
    path = 'apps/core/views.py'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(core_views_fixed)
    print("✅ Código corregido. Los nuevos registros no fallarán.")

if __name__ == "__main__":
    fix_missing_profiles() # Arregla la BD
    apply_code_fix()       # Arregla el Código