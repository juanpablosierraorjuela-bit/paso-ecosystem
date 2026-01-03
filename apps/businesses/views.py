from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from .models import Salon, Service, Employee, SalonSchedule, EmployeeSchedule
from .forms import OwnerRegistrationForm, SalonForm, ServiceForm, EmployeeForm, EmployeeCreationForm

User = get_user_model()

# --- PÚBLICO ---
def home(request):
    return render(request, 'home.html')
def marketplace(request):
    salons = Salon.objects.all()
    return render(request, 'marketplace.html', {'salons': salons})
def salon_detail(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    return render(request, 'salon_detail.html', {'salon': salon})
def landing_businesses(request):
    return render(request, 'landing_businesses.html')

# --- REGISTRO ---
class RegisterOwnerView(CreateView):
    template_name = 'registration/register_owner.html'
    form_class = OwnerRegistrationForm
    success_url = '/dashboard/'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context: context['user_form'] = OwnerRegistrationForm()
        if 'salon_form' not in context: context['salon_form'] = SalonForm()
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
            SalonSchedule.objects.create(salon=salon)
            login(request, user)
            return redirect('owner_dashboard')
        return render(request, self.template_name, {'user_form': user_form, 'salon_form': salon_form})

# --- DASHBOARDS ---
@login_required
def dashboard_redirect(request):
    # Redirige según el tipo de usuario
    if hasattr(request.user, 'salon'):
        return redirect('owner_dashboard')
    elif hasattr(request.user, 'employee_profile'):
        return redirect('employee_dashboard')
    else:
        # Cliente o Admin
        return redirect('home')

@method_decorator(login_required, name='dispatch')
class OwnerDashboardView(TemplateView):
    template_name = 'dashboard/owner_dashboard.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try: context['salon'] = self.request.user.salon
        except Salon.DoesNotExist: context['salon'] = None
        return context

@login_required
def employee_dashboard(request):
    employee = request.user.employee_profile
    return render(request, 'employee_dashboard.html', {'employee': employee})

# --- CRUD EMPLEADOS (DUEÑO) ---
@method_decorator(login_required, name='dispatch')
class OwnerEmployeesView(ListView):
    model = Employee
    template_name = 'dashboard/owner_employees.html'
    context_object_name = 'employees'
    def get_queryset(self):
        return Employee.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeCreationForm
    template_name = 'dashboard/employee_form.html'
    success_url = reverse_lazy('owner_employees')

    def form_valid(self, form):
        # 1. Crear el Usuario de Login
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # 2. Crear el Perfil de Empleado
        employee = form.save(commit=False)
        employee.salon = self.request.user.salon
        employee.user = user
        employee.save()
        
        # 3. Crear Horario por defecto
        EmployeeSchedule.objects.create(employee=employee)
        
        return super().form_valid(form)

# --- SERVICIOS Y CONFIGURACIÓN ---
@method_decorator(login_required, name='dispatch')
class OwnerServicesView(ListView):
    model = Service
    template_name = 'dashboard/owner_services.html'
    context_object_name = 'services'
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')
    def form_valid(self, form):
        service = form.save(commit=False)
        service.salon = self.request.user.salon
        service.save()
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'dashboard/service_confirm_delete.html'
    success_url = reverse_lazy('owner_services')
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class OwnerSettingsView(UpdateView):
    model = SalonSchedule
    template_name = 'dashboard/owner_settings.html'
    fields = ['monday_open', 'tuesday_open', 'wednesday_open', 'thursday_open', 'friday_open', 'saturday_open', 'sunday_open']
    success_url = reverse_lazy('owner_settings')
    def get_object(self, queryset=None):
        salon = self.request.user.salon
        schedule, created = SalonSchedule.objects.get_or_create(salon=salon)
        return schedule
