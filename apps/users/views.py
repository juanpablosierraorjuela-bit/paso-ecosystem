¿from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

# --- CORRECCIÓN: Usar SalonForm (el nombre correcto) ---
# O simplemente no importarlo si no se usa, para evitar errores.
# En este caso, limpiamos para que sea seguro.

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get('role'):
                user.role = form.cleaned_data.get('role')
            user.save()
            login(request, user)
            
            # Redirección segura
            if getattr(user, 'role', '') == 'OWNER' or getattr(user, 'role', '') == 'ADMIN':
                return redirect('dashboard') 
            else:
                return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Vistas auxiliares para evitar errores de importación en urls.py
def dashboard_view(request): return redirect('dashboard')
def accept_invite_view(request): return redirect('home')
def employee_join_view(request): return redirect('home')
def create_salon_view(request): return redirect('dashboard')