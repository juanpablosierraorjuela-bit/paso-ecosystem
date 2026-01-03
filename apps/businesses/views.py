from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.urls import reverse_lazy
from .models import Salon, Service, Employee, SalonSchedule
from .forms import OwnerRegistrationForm, SalonForm, ServiceForm, EmployeeForm

# --- PÚBLICO ---

def home(request):
    return render(request, 'home.html')

def marketplace(request):
    salons = Salon.objects.all()
    return render(request, 'marketplace.html', {'salons': salons})

def salon_detail(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    return render(request, 'salon_detail.html', {'salon': salon})

# --- REGISTRO (ARREGLADO: Redirige al Dashboard) ---

class RegisterOwnerView(CreateView):
    template_name = 'registration/register_owner.html'
    form_class = OwnerRegistrationForm
    success_url = '/dashboard/'  # <--- AQUÍ ESTÁ EL CAMBIO CLAVE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = OwnerRegistrationForm()
        if 'salon_form' not in context:
            context['salon_form'] = SalonForm()
        return context

    def post(self, request, *args, **kwargs):
        user_form = OwnerRegistrationForm(request.POST)
        salon_form = SalonForm(request.POST)
        
        if user_form.is_valid() and salon_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            salon = salon_form.save(commit=False)
            salon.owner = user
            salon.save()
            
            # Crear horario por defecto
            SalonSchedule.objects.create(salon=salon)
            
            login(request, user)
            return redirect('owner_dashboard') # Redirección explícita
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'salon_form': salon_form
        })

# --- PANEL DE DUEÑO (DASHBOARD) ---

@method_decorator(login_required, name='dispatch')
class OwnerDashboardView(TemplateView):
    template_name = 'dashboard/owner_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Intentar obtener el salón del usuario actual
        try:
            context['salon'] = self.request.user.salon
        except Salon.DoesNotExist:
            context['salon'] = None
        return context

@method_decorator(login_required, name='dispatch')
class OwnerServicesView(ListView):
    model = Service
    template_name = 'dashboard/owner_services.html'
    context_object_name = 'services'

    def get_queryset(self):
        return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class OwnerEmployeesView(ListView):
    model = Employee
    template_name = 'dashboard/owner_employees.html'
    context_object_name = 'employees'

    def get_queryset(self):
        return Employee.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class OwnerSettingsView(UpdateView):
    model = SalonSchedule
    template_name = 'dashboard/owner_settings.html'
    fields = ['monday_open', 'tuesday_open', 'wednesday_open', 'thursday_open', 'friday_open', 'saturday_open', 'sunday_open']
    success_url = reverse_lazy('owner_settings')

    def get_object(self, queryset=None):
        # Obtiene o crea el horario del salón del usuario
        salon = self.request.user.salon
        schedule, created = SalonSchedule.objects.get_or_create(salon=salon)
        return schedule


# --- VISTA RECUPERADA ---
def landing_businesses(request):
    return render(request, 'landing_businesses.html')
