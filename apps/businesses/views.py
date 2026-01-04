from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from datetime import datetime
from django.contrib import messages
from django.http import JsonResponse

from .models import Salon, Service, Employee, Booking, EmployeeSchedule
from .forms import SalonForm, ServiceForm, EmployeeForm, OwnerSignUpForm
from .logic import get_available_slots

# --- PÚBLICO ---
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
        if query: queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
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

# --- BOOKING WIZARD ---
class BookingWizardStartView(View):
    def post(self, request):
        request.session['booking_salon_id'] = request.POST.get('salon_id')
        request.session['booking_service_id'] = request.POST.get('service_id')
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
    
    # Calcular Abono Dinámico
    deposit = service.price * (salon.deposit_percentage / 100)
    
    return render(request, 'booking/step_confirm.html', {
        'service': service, 'salon': salon, 'deposit': deposit,
        'date': request.session.get('booking_date'),
        'time': request.session.get('booking_time')
    })

def booking_create(request):
    if request.method == 'POST':
        # Recuperar datos sesión
        salon_id = request.session.get('booking_salon_id')
        service_id = request.session.get('booking_service_id')
        employee_id = request.session.get('booking_employee_id')
        
        # Recuperar datos formulario
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        
        # Procesar Fecha
        dt_str = f"{request.session.get('booking_date')} {request.session.get('booking_time')}"
        full_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        
        service = get_object_or_404(Service, id=service_id)
        
        # Lógica Lazy User (Aquí podríamos crear un User real, por ahora solo cita)
        booking = Booking.objects.create(
            salon_id=salon_id, service_id=service_id, employee_id=employee_id,
            customer_name=customer_name, customer_phone=customer_phone,
            date_time=full_dt, total_price=service.price,
            # El deposit se calcula solo en el modelo save()
        )
        return redirect('booking_success', booking_id=booking.id)
    return redirect('marketplace')

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # MENSAJE DE WHATSAPP AUTOMATIZADO Y DETALLADO
    saldo = booking.total_price - booking.deposit_amount
    msg = f"Hola *{booking.salon.name}* , soy {booking.customer_name}.%0A%0A" \
          f" *Nueva Reserva:* {booking.date_time.strftime('%d/%m %H:%M')}%0A" \
          f" *Servicio:* {booking.service.name}%0A" \
          f" *Profesional:* {booking.employee.name}%0A%0A" \
          f" *Total:* %0A" \
          f" *Abono a Pagar:* %0A" \
          f" *Restante en local:* %0A%0A" \
          f"¿A qué cuenta (Nequi/Bancolombia) transfiero el abono?"
    
    wa_link = f"https://wa.me/{booking.salon.whatsapp_number}?text={msg}"
    
    return render(request, 'booking/success.html', {'booking': booking, 'wa_link': wa_link})

# --- DUEÑO: VERIFICACIÓN DE PAGOS ---
class OwnerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/owner_dashboard.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        salon = self.request.user.salon
        # Obtener citas ordenadas
        ctx['pending_bookings'] = Booking.objects.filter(salon=salon, status='PENDING_PAYMENT').order_by('date_time')
        ctx['confirmed_bookings'] = Booking.objects.filter(salon=salon, status='VERIFIED').order_by('date_time')
        return ctx

@LoginRequiredMixin
def verify_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, salon__owner=request.user)
    booking.status = 'VERIFIED'
    booking.save()
    # Aquí podríamos redirigir a WhatsApp para confirmar al cliente
    return redirect('owner_dashboard')

# --- REGISTRO Y GESTIÓN (CRUDs Standard) ---
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
        form.instance.salon = self.request.user.salon
        employee = form.save(commit=False)
        employee.save()
        EmployeeSchedule.objects.create(employee=employee)
        return redirect('owner_employees')

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

class OwnerSettingsView(LoginRequiredMixin, UpdateView):
    model = Salon
    form_class = SalonForm
    template_name = 'dashboard/owner_settings.html'
    success_url = reverse_lazy('owner_dashboard')
    def get_object(self): return self.request.user.salon
