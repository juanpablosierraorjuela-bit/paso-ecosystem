from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, date, time
from django.contrib import messages

from .models import Salon, Service, Employee, SalonSchedule, EmployeeSchedule, Booking
from .forms import (
    OwnerRegistrationForm, SalonForm, ServiceForm, 
    EmployeeForm, EmployeeCreationForm, SalonScheduleForm
)

User = get_user_model()

# ... (Vistas generales mantenidas) ...
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

# --- REGISTRO (CON LA LÓGICA DE WHATSAPP AUTOMÁTICO) ---
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
            # Lógica rescatada: Si ponen teléfono, se asume WhatsApp
            salon.whatsapp = salon_form.cleaned_data['phone']
            salon.save()
            SalonSchedule.objects.create(salon=salon)
            login(request, user)
            return redirect('owner_dashboard')
        return render(request, self.template_name, {'user_form': user_form, 'salon_form': salon_form})

# --- DASHBOARD ---
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

# --- CONFIGURACIÓN (LÓGICA MEJORADA) ---
@login_required
def owner_settings_view(request):
    try:
        salon = request.user.salon
    except Salon.DoesNotExist:
        return redirect('home')

    schedule, created = SalonSchedule.objects.get_or_create(salon=salon)

    if request.method == 'POST':
        salon_form = SalonForm(request.POST, instance=salon)
        schedule_form = SalonScheduleForm(request.POST, instance=schedule)

        if salon_form.is_valid() and schedule_form.is_valid():
            salon_obj = salon_form.save(commit=False)
            # Aseguramos que el WhatsApp se actualice si cambian el teléfono
            if salon_obj.phone:
                salon_obj.whatsapp = salon_obj.phone
            salon_obj.save()
            schedule_form.save()
            messages.success(request, '¡Tu negocio se ha actualizado correctamente!')
            return redirect('owner_settings')
        else:
            messages.error(request, 'Hubo un error. Revisa los campos en rojo.')
    else:
        salon_form = SalonForm(instance=salon)
        schedule_form = SalonScheduleForm(instance=schedule)

    return render(request, 'dashboard/owner_settings.html', {
        'salon_form': salon_form,
        'schedule_form': schedule_form
    })

class OwnerSettingsView(TemplateView):
    def as_view(self=None, **initkwargs):
        return owner_settings_view

# --- VISTAS CRUD DE SERVICIOS Y EMPLEADOS ---
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

@login_required
def employee_dashboard(request):
    return render(request, 'employee_dashboard.html', {'employee': request.user.employee_profile})
