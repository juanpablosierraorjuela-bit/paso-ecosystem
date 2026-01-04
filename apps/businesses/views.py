from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, date, time
from .models import Salon, Service, Employee, SalonSchedule, EmployeeSchedule, Booking
from .forms import (
    OwnerRegistrationForm, SalonForm, ServiceForm, 
    EmployeeForm, EmployeeCreationForm, SalonScheduleForm
)

User = get_user_model()

# --- VISTA DE REGISTRO MEJORADA ---
class RegisterOwnerView(CreateView):
    template_name = 'registration/register_owner.html'
    form_class = OwnerRegistrationForm
    success_url = '/dashboard/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_form'] = OwnerRegistrationForm()
        ctx['salon_form'] = SalonForm()
        return ctx

    def post(self, request, *args, **kwargs):
        user_form = OwnerRegistrationForm(request.POST)
        salon_form = SalonForm(request.POST)
        
        if user_form.is_valid() and salon_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            salon = salon_form.save(commit=False)
            salon.owner = user
            
            # TRUCO: Copiamos el teléfono al campo whatsapp automáticamente
            salon.whatsapp = salon_form.cleaned_data['phone']
            
            salon.save()
            SalonSchedule.objects.create(salon=salon)
            login(request, user)
            return redirect('owner_dashboard')
        
        return render(request, self.template_name, {'user_form': user_form, 'salon_form': salon_form})

# --- OTRAS VISTAS (MANTENIDAS) ---
def home(request): return render(request, 'home.html')
def marketplace(request): return render(request, 'marketplace.html', {'salons': Salon.objects.all()})
def salon_detail(request, salon_id): return render(request, 'salon_detail.html', {'salon': get_object_or_404(Salon, id=salon_id)})
def landing_businesses(request): return render(request, 'landing_businesses.html')

@login_required
def booking_wizard(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    return render(request, 'booking/step_calendar.html', {'salon': salon})

@login_required
def client_dashboard(request):
    bookings = Booking.objects.filter(customer=request.user).order_by('-date')
    return render(request, 'client_dashboard.html', {'bookings': bookings})

@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'salon'): return redirect('owner_dashboard')
    elif hasattr(request.user, 'employee_profile'): return redirect('employee_dashboard')
    else: return redirect('client_dashboard')

@method_decorator(login_required, name='dispatch')
class OwnerDashboardView(TemplateView):
    template_name = 'dashboard/owner_dashboard.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try: ctx['salon'] = self.request.user.salon
        except: ctx['salon'] = None
        if ctx['salon']:
            ctx['pending_bookings'] = Booking.objects.filter(salon=ctx['salon'], status='pending')
        return ctx

@method_decorator(login_required, name='dispatch')
class OwnerServicesView(ListView):
    model = Service
    template_name = 'dashboard/owner_services.html'
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')
    def form_valid(self, form):
        form.instance.salon = self.request.user.salon
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
    success_url = reverse_lazy('owner_services')
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class OwnerEmployeesView(ListView):
    model = Employee
    template_name = 'dashboard/owner_employees.html'
    def get_queryset(self): return Employee.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeCreationForm
    template_name = 'dashboard/employee_form.html'
    success_url = reverse_lazy('owner_employees')
    def form_valid(self, form):
        user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'])
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        employee = form.save(commit=False)
        employee.salon = self.request.user.salon
        employee.user = user
        employee.save()
        EmployeeSchedule.objects.create(employee=employee)
        return super().form_valid(form)
        
@method_decorator(login_required, name='dispatch')
class OwnerSettingsView(UpdateView):
    model = SalonSchedule
    template_name = 'dashboard/owner_settings.html'
    form_class = SalonScheduleForm
    success_url = reverse_lazy('owner_settings')
    def get_object(self, queryset=None):
        schedule, created = SalonSchedule.objects.get_or_create(salon=self.request.user.salon)
        return schedule

@login_required
def employee_dashboard(request):
    return render(request, 'employee_dashboard.html', {'employee': request.user.employee_profile})
