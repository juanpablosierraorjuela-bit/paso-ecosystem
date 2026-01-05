from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from .forms import OwnerRegistrationForm
from django.urls import reverse_lazy
from .models import User
from django.utils import timezone

# --- LANDING DE DOLORES (MARKETING) ---
def pain_landing(request):
    return render(request, 'landing/pain_points.html')

# --- REGISTRO ---
class OwnerRegisterView(CreateView):
    model = User
    form_class = OwnerRegistrationForm
    template_name = 'registration/register_owner.html'
    success_url = reverse_lazy('home') # Redirige al login/home tras registro

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = User.Role.OWNER
        user.save()
        return super().form_valid(form)

def home(request):
    return render(request, 'home.html')

# --- EL PORTERO (DISPATCHER) ---
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
