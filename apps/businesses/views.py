from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Salon, Service, Employee, Booking
from .forms import SalonForm, ServiceForm, EmployeeForm

def home(request):
    return render(request, 'home.html')

class LandingBusinessesView(TemplateView):
    template_name = 'landing_businesses.html'

class RegisterOwnerView(TemplateView):
    template_name = 'registration/register_owner.html'

class MarketplaceView(ListView):
    model = Salon
    template_name = 'marketplace.html'
    context_object_name = 'salons'

    def get_queryset(self):
        query = self.request.GET.get('q')
        city = self.request.GET.get('city')
        
        queryset = Salon.objects.all()

        if city and city != 'Todas':
            queryset = queryset.filter(city__iexact=city)

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ciudades únicas y ordenadas para el filtro
        cities = Salon.objects.values_list('city', flat=True).distinct()
        context['cities'] = sorted(list(set(filter(None, cities))))
        return context

class SalonDetailView(DetailView):
    model = Salon
    template_name = 'salon_detail.html'
    context_object_name = 'salon'

class OwnerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/owner_dashboard.html'

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
        return super().form_valid(form)

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
