from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import OwnerRegistrationForm

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Iniciar sesión automáticamente
            login(request, user)
            messages.success(request, '¡Bienvenido! Tu ecosistema ha sido creado. Tienes 24h para activarlo.')
            return redirect('dashboard') # Redirige al panel de dueño
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = OwnerRegistrationForm()
    
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    return render(request, 'registration/login.html')

# --- SEMÁFORO DE BIENVENIDA ---
from django.contrib.auth.decorators import login_required

@login_required
def dispatch_user(request):
    user = request.user
    
    # 1. Si es Dueño -> Panel de Negocio (Ruta 'dashboard' de businesses)
    if user.role == 'OWNER':
        return redirect('dashboard')
    
    # 2. Si es Cliente -> Marketplace (Ruta 'marketplace_home' de marketplace)
    elif user.role == 'CLIENT':
        return redirect('marketplace_home')
        
    # 3. Si es Empleado -> Su Agenda (Ruta actual de lista de empleados)
    # Nota: Cuando creemos el dashboard de empleado en Fase 3, cambiaremos esto a 'employee_dashboard'
    elif user.role == 'EMPLOYEE':
        return redirect('employee_dashboard')  # CORREGIDO: Panel del Empleado
        
    # 4. Si eres TÚ (Superuser) -> Admin de Django
    elif user.is_superuser:
        return redirect('/admin/')
        
    else:
        return redirect('home')
