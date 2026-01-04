from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Q
from datetime import datetime
from django.contrib import messages
from apps.core_saas.models import User
from .models import Salon, Service, Employee, Booking, EmployeeSchedule
from .forms import SalonForm, ServiceForm, EmployeeForm, OwnerSignUpForm, EmployeeScheduleForm
from .logic import get_available_slots

def home(request): return render(request, 'home.html')

class MarketplaceView(ListView):
    model = Salon
    template_name = 'marketplace.html'
    context_object_name = 'salons'
    def get_queryset(self):
        query = self.request.GET.get('q')
        city = self.request.GET.get('city')
        queryset = Salon.objects.all()
        if city and city != 'Todas': queryset = queryset.filter(city__iexact=city)
        if query: queryset = queryset.filter(Q(name__icontains=query))
        return queryset
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cities = Salon.objects.values_list('city', flat=True).distinct()
        ctx['cities'] = sorted(list(set(filter(None, cities))))
        return ctx

class SalonDetailView(DetailView):
    model = Salon
    template_name = 'salon_detail.html'
    context_object_name = 'salon'

class LandingBusinessesView(TemplateView): template_name = 'landing_businesses.html'

class BookingWizardStartView(View):
    def post(self, request):
        salon_id = request.POST.get('salon_id')
        service_id = request.POST.get('service_id')
        if not service_id:
            messages.error(request, 'Debes seleccionar un servicio.')
            return redirect('salon_detail', pk=salon_id)
        request.session['booking_salon_id'] = salon_id
        request.session['booking_service_id'] = service_id
        return redirect('booking_step_employee')

def booking_step_employee(request):
    salon_id = request.session.get('booking_salon_id')
    if not salon_id: return redirect('marketplace')
    employees = Employee.objects.filter(salon_id=salon_id, is_active=True)
    return render(request, 'booking/step_employee.html', {'employees': employees})

def booking_step_calendar(request):
    if request.method == 'POST': request.session['booking_employee_id'] = request.POST.get('employee_id')
    emp_id = request.session.get('booking_employee_id')
    srv_id = request.session.get('booking_service_id')
    if not emp_id: return redirect('booking_step_employee')
    employee = get_object_or_404(Employee, id=emp_id)
    service = get_object_or_404(Service, id=srv_id)
    date_str = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    slots = get_available_slots(employee, service, selected_date)
    return render(request, 'booking/step_calendar.html', {
        'employee': employee, 'service': service, 'slots': slots,
        'selected_date': date_str, 'today': datetime.now().strftime('%Y-%m-%d')
    })

def booking_step_confirm(request):
    if request.method == 'POST':
        request.session['booking_date'] = request.POST.get('date')
        request.session['booking_time'] = request.POST.get('time')
    srv_id = request.session.get('booking_service_id')
    salon_id = request.session.get('booking_salon_id')
    service = get_object_or_404(Service, id=srv_id)
    salon = get_object_or_404(Salon, id=salon_id)
    deposit = service.price * (salon.deposit_percentage / 100)
    return render(request, 'booking/step_confirm.html', {
        'service': service, 'salon': salon, 'deposit': deposit,
        'date': request.session.get('booking_date'), 'time': request.session.get('booking_time')
    })

def booking_create(request):
    if request.method == 'POST':
        salon_id = request.session.get('booking_salon_id')
        service_id = request.session.get('booking_service_id')
        employee_id = request.session.get('booking_employee_id')
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        dt_str = f"{request.session.get('booking_date')} {request.session.get('booking_time')}"
        full_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        service = get_object_or_404(Service, id=service_id)
        booking = Booking.objects.create(
            salon_id=salon_id, service_id=service_id, employee_id=employee_id,
            customer_name=customer_name, customer_phone=customer_phone,
            date_time=full_dt, total_price=service.price,
        )
        return redirect('booking_success', booking_id=booking.id)
    return redirect('marketplace')

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    msg = f"Hola *{booking.salon.name}*, soy {booking.customer_name}. Cita #{booking.id}. Abono: ."
    wa_link = f"https://wa.me/{booking.salon.whatsapp_number}?text={msg}"
    return render(request, 'booking/success.html', {'booking': booking, 'wa_link': wa_link})

class OwnerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/owner_dashboard.html'
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'EMPLOYEE':
            return redirect('employee_dashboard')
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        salon = self.request.user.salon
        ctx['pending_bookings'] = Booking.objects.filter(salon=salon, status='PENDING_PAYMENT').order_by('date_time')
        ctx['confirmed_bookings'] = Booking.objects.filter(salon=salon, status='VERIFIED').order_by('date_time')
        return ctx

@login_required
def verify_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, salon__owner=request.user)
    booking.status = 'VERIFIED'
    booking.save()
    return redirect('owner_dashboard')

class OwnerEmployeesView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'dashboard/owner_employees.html'
    context_object_name = 'employees'
    def get_queryset(self): return Employee.objects.filter(salon__owner=self.request.user)

class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'dashboard/employee_form.html'
    success_url = reverse_lazy('owner_employees')
    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = User.objects.create_user(username=username, email=f"{username}@paso.com", password=password)
        user.role = 'EMPLOYEE'
        user.save()
        employee = form.save(commit=False)
        employee.salon = self.request.user.salon
        employee.user = user
        employee.save()
        EmployeeSchedule.objects.create(employee=employee)
        return redirect('owner_employees')

@login_required
def employee_dashboard(request):
    if request.user.role != 'EMPLOYEE': return redirect('owner_dashboard')
    employee = request.user.employee_profile
    bookings = Booking.objects.filter(employee=employee, status='VERIFIED').order_by('date_time')
    return render(request, 'employee_dashboard.html', {'employee': employee, 'bookings': bookings})

@login_required
def employee_schedule_update(request):
    employee = request.user.employee_profile
    schedule = employee.schedule
    if request.method == 'POST':
        form = EmployeeScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Horario actualizado.')
            return redirect('employee_dashboard')
    else:
        form = EmployeeScheduleForm(instance=schedule)
    return render(request, 'dashboard/employee_schedule.html', {'form': form, 'salon': employee.salon})

class OwnerSettingsView(LoginRequiredMixin, UpdateView):
    model = Salon
    form_class = SalonForm
    template_name = 'dashboard/owner_settings.html'
    success_url = reverse_lazy('owner_dashboard')
    def get_object(self): return self.request.user.salon

class RegisterOwnerView(CreateView):
    template_name = 'registration/register_owner.html'
    form_class = OwnerSignUpForm
    success_url = reverse_lazy('saas_login')

class OwnerServicesView(LoginRequiredMixin, ListView):
    model = Service
    template_name = 'dashboard/owner_services.html'
    context_object_name = 'services'
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')
    def form_valid(self, form):
        form.instance.salon = self.request.user.salon
        return super().form_valid(form)

class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

class ServiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Service
    template_name = 'dashboard/service_confirm_delete.html'
    success_url = reverse_lazy('owner_services')
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'dashboard/employee_form.html'
    success_url = reverse_lazy('owner_employees')
    def get_queryset(self): return Employee.objects.filter(salon__owner=self.request.user)

class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'dashboard/employee_confirm_delete.html'
    success_url = reverse_lazy('owner_employees')
    def get_queryset(self): return Employee.objects.filter(salon__owner=self.request.user)
