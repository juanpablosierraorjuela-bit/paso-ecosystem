# --- SCRIPT DE REPARACIÓN AUTOMÁTICA (VERSIÓN WINDOWS/POWERSHELL) ---
Write-Host "🔧 INICIANDO REPARACIÓN DEL SISTEMA PASO BEAUTY..." -ForegroundColor Cyan

# 1. REESCRIBIR APPS/USERS/VIEWS.PY
$viewsContent = @"
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

from apps.businesses.models import Salon, Employee, Booking
from apps.businesses.forms import SalonCreateForm
from .forms import CustomUserCreationForm

def home(request):
    try:
        salons = list(Salon.objects.all().order_by('-id'))
    except:
        salons = []
    return render(request, 'home.html', {'salons': salons})

def register(request):
    """
    REGISTRO CENTRALIZADO
    """
    # 1. Recuperar token
    invite_token = request.GET.get('invite') or request.POST.get('invite_token')
    
    # 2. CASO: YA LOGUEADO
    if request.user.is_authenticated:
        if invite_token:
            request.session['pending_invite'] = invite_token
            return redirect('accept_invite')
        return redirect('dashboard')

    inviting_salon = None
    if invite_token:
        try:
            uuid_obj = uuid.UUID(str(invite_token))
            inviting_salon = Salon.objects.filter(invite_token=uuid_obj).first()
        except:
            pass

    # 3. CASO: REGISTRO NUEVO
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if invite_token:
                user.role = 'EMPLOYEE'
            user.save()
            login(request, user)

            if invite_token:
                request.session['pending_invite'] = invite_token
                return redirect('accept_invite')
            
            return redirect('dashboard')
    else:
        initial = {}
        if inviting_salon:
            initial = {'role': 'EMPLOYEE'}
        form = CustomUserCreationForm(initial=initial)

    return render(request, 'registration/register.html', {
        'form': form, 
        'inviting_salon': inviting_salon
    })

@login_required
def accept_invite_view(request):
    """
    PANTALLA INTERMEDIA: CONFIRMACIÓN
    """
    token = request.session.get('pending_invite')
    if not token:
        token = request.GET.get('invite') # Intento extra

    if not token:
        return redirect('dashboard')

    salon = None
    try:
        uuid_obj = uuid.UUID(str(token))
        salon = Salon.objects.filter(invite_token=uuid_obj).first()
    except:
        pass

    if not salon:
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            Employee.objects.get_or_create(
                user=request.user,
                salon=salon,
                defaults={
                    'name': f"{request.user.first_name} {request.user.last_name}" or request.user.username,
                    'phone': getattr(request.user, 'phone', '')
                }
            )
            request.user.role = 'EMPLOYEE'
            request.user.save()
            
            if 'pending_invite' in request.session:
                del request.session['pending_invite']
                
            messages.success(request, f"¡Bienvenido a {salon.name}!")
            return redirect('employee_settings')
            
        except Exception as e:
            logger.error(f"Error aceptando: {e}")
            return redirect('dashboard')

    return render(request, 'registration/accept_invite.html', {'salon': salon})

@login_required
def dashboard_view(request):
    user = request.user
    role = getattr(user, 'role', 'CUSTOMER') 

    if role == 'EMPLOYEE':
        if hasattr(user, 'employee'):
            return redirect('employee_settings')
        return redirect('employee_join')

    elif role in ['ADMIN', 'OWNER'] or getattr(user, 'is_business_owner', False):
        try:
            salon = Salon.objects.filter(owner=user).first()
            if not salon:
                return redirect('create_salon')
            return render(request, 'dashboard/index.html', {'salon': salon})
        except:
            return redirect('create_salon')

    else:
        bookings = []
        try:
            bookings = list(Booking.objects.filter(customer=user).order_by('-start_time'))
        except:
            bookings = []
        return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def employee_join_view(request):
    return render(request, 'registration/employee_join.html')

@login_required
def create_salon_view(request):
    if Salon.objects.filter(owner=request.user).exists():
        return redirect('dashboard')
    if request.method == 'POST':
        form = SalonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            salon = form.save(commit=False)
            salon.owner = request.user
            salon.save()
            return redirect('dashboard')
    else:
        form = SalonCreateForm()
    return render(request, 'dashboard/create_salon.html', {'form': form})

def salon_detail(request, slug):
    from apps.businesses.views import salon_detail as business_salon_detail
    return business_salon_detail(request, slug)
"@
Set-Content -Path "apps/users/views.py" -Value $viewsContent -Encoding UTF8
Write-Host "✅ apps/users/views.py actualizado." -ForegroundColor Green

# 2. REESCRIBIR CONFIG/URLS.PY
$urlsContent = @"
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from apps.users import views as user_views
from apps.businesses import views as biz_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # RUTA CRÍTICA
    path('accept-invite/', user_views.accept_invite_view, name='accept_invite'),

    path('dashboard/', user_views.dashboard_view, name='dashboard'),
    path('dashboard/join/', user_views.employee_join_view, name='employee_join'),
    path('dashboard/create-salon/', user_views.create_salon_view, name='create_salon'),
    path('dashboard/settings/', biz_views.salon_settings_view, name='salon_settings'),
    path('dashboard/employee/', biz_views.employee_settings_view, name='employee_settings'),
    path('salon/<slug:slug>/', biz_views.salon_detail, name='salon_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"@
Set-Content -Path "config/urls.py" -Value $urlsContent -Encoding UTF8
Write-Host "✅ config/urls.py actualizado." -ForegroundColor Green

# 3. CREAR TEMPLATE ACCEPT_INVITE.HTML
$acceptInviteContent = @"
{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card shadow-lg border-0 rounded-4 text-center overflow-hidden">
                <div class="card-header bg-primary text-white py-4">
                    <h3 class="fw-bold mb-0">🎉 ¡Invitación Oficial!</h3>
                </div>
                <div class="card-body p-5">
                    {% if salon.logo %}
                        <img src="{{ salon.logo.url }}" class="rounded-circle shadow mb-3" style="width: 100px; height: 100px; object-fit: cover; margin-top: -60px; border: 4px solid white;">
                    {% else %}
                        <div class="rounded-circle bg-white text-primary d-flex align-items-center justify-content-center mx-auto shadow mb-3" style="width: 100px; height: 100px; font-size: 2.5rem; margin-top: -60px; border: 4px solid white; font-weight: bold;">
                            {{ salon.name|slice:":1" }}
                        </div>
                    {% endif %}
                    <h4 class="fw-bold mb-1">{{ salon.name }}</h4>
                    <p class="text-muted small mb-4">Te invita a unirte como Profesional.</p>
                    
                    <form method="post">
                        {% csrf_token %}
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary btn-lg rounded-pill fw-bold shadow-sm">
                                ✅ Aceptar y Entrar
                            </button>
                            <a href="{% url 'dashboard' %}" class="btn btn-link text-muted text-decoration-none small">Cancelar</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"@
New-Item -ItemType Directory -Force -Path "templates/registration" | Out-Null
Set-Content -Path "templates/registration/accept_invite.html" -Value $acceptInviteContent -Encoding UTF8
Write-Host "✅ templates/registration/accept_invite.html creado." -ForegroundColor Green

# 4. REESCRIBIR REGISTER.HTML
$registerContent = @"
{% extends 'base.html' %}
{% block content %}
<div class="container d-flex align-items-center justify-content-center" style="min-height: 80vh;">
    <div class="col-md-5 col-lg-4">
        <div class="text-center mb-4">
            <h3 class="fw-bold">Crear Cuenta</h3>
            {% if inviting_salon %}
                <div class="badge bg-primary-subtle text-primary px-3 py-2 rounded-pill mt-2">
                    <i class="bi bi-shop me-1"></i> Registrándose en: <strong>{{ inviting_salon.name }}</strong>
                </div>
            {% else %}
                <p class="text-muted">Únete a PASO Beauty.</p>
            {% endif %}
        </div>
        <div class="card-premium p-4 shadow-lg bg-white rounded-4 border-0">
            <form method="post">
                {% csrf_token %}
                
                {% if inviting_salon %}
                    <input type="hidden" name="invite_token" value="{{ inviting_salon.invite_token }}">
                {% endif %}
                
                {% for field in form %}
                    {% if field.name == 'role' and inviting_salon %}
                        <div class="d-none">{{ field }}</div>
                    {% else %}
                        <div class="mb-3">
                            <label class="form-label fw-bold small text-muted">{{ field.label }}</label>
                            {{ field }}
                            {% if field.errors %}<div class="text-danger small mt-1">{{ field.errors.0 }}</div>{% endif %}
                        </div>
                    {% endif %}
                {% endfor %}
                
                <button type="submit" class="btn btn-primary w-100 py-3 mt-2 fw-bold rounded-pill shadow-sm">
                    Continuar <i class="bi bi-arrow-right-short"></i>
                </button>
            </form>
            <div class="text-center mt-4 border-top pt-3">
                <span class="text-muted small">¿Ya tienes cuenta?</span>
                <a href="{% url 'login' %}" class="text-primary fw-bold text-decoration-none ms-1">Inicia Sesión</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"@
Set-Content -Path "templates/registration/register.html" -Value $registerContent -Encoding UTF8
Write-Host "✅ templates/registration/register.html actualizado." -ForegroundColor Green

# 5. SUBIR A GITHUB
Write-Host "🚀 SUBIENDO CAMBIOS A GITHUB..." -ForegroundColor Yellow
git add .
git commit -m "Fix: Script PowerShell - Sistema de Invitaciones Completo y Reparado"
git push origin main

Write-Host "✨ ¡LISTO! Despliegue iniciado en Render." -ForegroundColor Cyan