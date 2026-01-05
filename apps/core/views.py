from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from .forms import OwnerRegistrationForm
from django.urls import reverse_lazy
from .models import User

# --- REGISTRO DE DUEÑOS ---
class OwnerRegisterView(CreateView):
    model = User
    form_class = OwnerRegistrationForm
    template_name = 'registration/register_owner.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = User.Role.OWNER
        user.save()
        return super().form_valid(form)

# --- HOME ---
def home(request):
    return render(request, 'home.html')

# --- DISPATCHER: EL CEREBRO DE REDIRECCIÓN ---
@login_required
def dashboard_redirect(request):
    """
    Esta función decide a dónde va el usuario según su rol
    después de iniciar sesión.
    """
    user = request.user
    
    if user.role == User.Role.OWNER:
        return redirect('businesses:dashboard')
    elif user.role == User.Role.EMPLOYEE:
        return redirect('booking:employee_dashboard')
    elif user.role == User.Role.CLIENT:
        return redirect('booking:client_dashboard')
    elif user.is_staff or user.is_superuser:
        return redirect('/admin/')
    
    # Si no tiene rol definido, al home
    return redirect('home')
