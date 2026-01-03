import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
REQ_PATH = os.path.join(BASE_DIR, "requirements.txt")

FORMS_PATH = os.path.join(APP_DIR, "forms.py")
VIEWS_PATH = os.path.join(APP_DIR, "views.py")
URLS_PATH = os.path.join(APP_DIR, "urls.py")

# --- 1. SOBRESCRIBIR REQUIREMENTS.TXT (Sin leer el anterior) ---
def crear_requirements_limpio():
    print("🧹 1. Creando requirements.txt limpio y ligero...")
    # Lista esencial para que tu proyecto vuele en Render
    contenido = """Django>=5.0
gunicorn
psycopg2-binary
dj-database-url
whitenoise
pillow
django-cors-headers
django-jazzmin
djangorestframework
django-multitenant
"""
    # Usamos 'wb' (escritura binaria) para evitar problemas de codificación raros
    with open(REQ_PATH, "wb") as f:
        f.write(contenido.encode('utf-8'))
    print("   -> requirements.txt regenerado exitosamente.")

# --- 2. REESCRIBIR FORMS.PY ---
CONTENIDO_FORMS = """from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee

User = get_user_model()

class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Crea una contraseña segura'
    }), label="Contraseña")
    
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Repite la contraseña'
    }), label="Confirmar Contraseña")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario para iniciar sesión'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'address', 'phone', 'whatsapp', 'instagram']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Estética Divina'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle 123 # 45-67, Bogotá'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono fijo o celular'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+57 300 123 4567'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'tu_usuario_instagram'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte de Cabello'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles del servicio...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 30'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 25000'}),
        }
        labels = {
            'name': 'Nombre del Servicio',
            'description': 'Descripción',
            'duration_minutes': 'Duración (minutos)',
            'price': 'Precio ($)',
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
"""

# --- 3. REESCRIBIR VIEWS.PY ---
CONTENIDO_VIEWS = """from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DeleteView
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

def landing_businesses(request):
    return render(request, 'landing_businesses.html')

# --- REGISTRO ---
class RegisterOwnerView(CreateView):
    template_name = 'registration/register_owner.html'
    form_class = OwnerRegistrationForm
    success_url = '/dashboard/'

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
            
            SalonSchedule.objects.create(salon=salon)
            
            login(request, user)
            return redirect('owner_dashboard')
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'salon_form': salon_form
        })

# --- DASHBOARD DUEÑO ---
@method_decorator(login_required, name='dispatch')
class OwnerDashboardView(TemplateView):
    template_name = 'dashboard/owner_dashboard.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        salon = self.request.user.salon
        schedule, created = SalonSchedule.objects.get_or_create(salon=salon)
        return schedule

# --- CRUD SERVICIOS ---
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
    def get_queryset(self):
        return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'dashboard/service_confirm_delete.html'
    success_url = reverse_lazy('owner_services')
    def get_queryset(self):
        return Service.objects.filter(salon__owner=self.request.user)
"""

# --- 4. REESCRIBIR URLS.PY ---
CONTENIDO_URLS = """from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Públicas
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('salon/<int:salon_id>/', views.salon_detail, name='salon_detail'),
    path('negocios/', views.landing_businesses, name='landing_businesses'),
    
    # Autenticación
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register_owner/', views.RegisterOwnerView.as_view(), name='register_owner'),

    # Dashboard Dueño
    path('dashboard/', views.OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('dashboard/services/', views.OwnerServicesView.as_view(), name='owner_services'),
    path('dashboard/employees/', views.OwnerEmployeesView.as_view(), name='owner_employees'),
    path('dashboard/settings/', views.OwnerSettingsView.as_view(), name='owner_settings'),

    # CRUD Servicios
    path('dashboard/services/add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('dashboard/services/edit/<int:pk>/', views.ServiceUpdateView.as_view(), name='service_edit'),
    path('dashboard/services/delete/<int:pk>/', views.ServiceDeleteView.as_view(), name='service_delete'),
]
"""

def reescribir_archivos():
    print("📝 2. Reescribiendo forms.py...")
    with open(FORMS_PATH, "wb") as f:
        f.write(CONTENIDO_FORMS.encode('utf-8'))

    print("🧠 3. Reescribiendo views.py...")
    with open(VIEWS_PATH, "wb") as f:
        f.write(CONTENIDO_VIEWS.encode('utf-8'))

    print("🔗 4. Reescribiendo urls.py...")
    with open(URLS_PATH, "wb") as f:
        f.write(CONTENIDO_URLS.encode('utf-8'))

if __name__ == "__main__":
    print("🛡️ INICIANDO REPARACIÓN BLINDADA 🛡️")
    crear_requirements_limpio()
    reescribir_archivos()
    print("\n✅ ¡Ahora SÍ! Archivos regenerados correctamente.")