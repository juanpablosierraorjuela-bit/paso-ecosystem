from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.text import slugify
from .forms import OwnerSignupForm, ClientSignupForm, CreateSalonForm
from .mixins import AdminRequiredMixin, EmployeeRequiredMixin
from apps.businesses.models import Salon

# --- LOGINS Y REGISTROS ---

class SaasLoginView(LoginView):
    template_name = 'registration/login.html'
    def get_success_url(self):
        user = self.request.user
        if user.role == 'ADMIN': return '/admin-dashboard/'
        elif user.role == 'EMPLOYEE': return '/employee-panel/'
        else: return '/marketplace/'

class OwnerSignupView(CreateView):
    form_class = OwnerSignupForm
    template_name = 'registration/registro_owner.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user) # Loguear automáticamente
        return redirect('crear_salon') # <--- PASO 2: CREAR NEGOCIO

class ClientSignupView(CreateView):
    form_class = ClientSignupForm
    template_name = 'registration/registro_cliente.html'
    success_url = reverse_lazy('marketplace')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('marketplace')

# --- FLUJO DE NEGOCIO ---

class CreateSalonView(LoginRequiredMixin, CreateView):
    '''Vista obligatoria para dueños nuevos'''
    form_class = CreateSalonForm
    template_name = 'core_saas/crear_salon.html'
    success_url = reverse_lazy('admin_dashboard')

    def form_valid(self, form):
        salon = form.save(commit=False)
        salon.owner = self.request.user # 1. Asignar Dueño
        
        # 2. Generar SLUG Único (ej: 'peluqueria-juan', 'peluqueria-juan-2')
        base_slug = slugify(salon.name)
        slug = base_slug
        counter = 1
        while Salon.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        salon.slug = slug
        
        salon.save()
        return redirect(self.success_url)

# --- PANELES ---
class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "core_saas/admin_dashboard.html"

class EmployeePanelView(EmployeeRequiredMixin, TemplateView):
    template_name = "core_saas/employee_panel.html"
    
# Vista Placeholder para empleados
from .forms import forms
class CreateEmployeeView(AdminRequiredMixin, CreateView):
    template_name = 'core_saas/crear_empleado.html'
    fields = '__all__' 
