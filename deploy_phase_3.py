import os
import subprocess

# --- 1. FORMULARIOS INTELIGENTES (Validación de Horas) ---
forms_content = """from django import forms
from .models import Service, OperatingHour

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'buffer_minutes', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte Clásico'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción para el buscador semántico...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'buffer_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tiempo de limpieza'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class OperatingHourForm(forms.ModelForm):
    class Meta:
        model = OperatingHour
        fields = ['day_of_week', 'opening_time', 'closing_time', 'is_closed']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        opening = cleaned_data.get('opening_time')
        closing = cleaned_data.get('closing_time')
        is_closed = cleaned_data.get('is_closed')

        if not is_closed and opening and closing:
            # Lógica para permitir amanecida:
            # Si cierra a las 02:00 y abre a las 22:00, es válido (cruza medianoche).
            pass 
        return cleaned_data
"""

# --- 2. VISTAS (Lógica de Negocio) ---
views_content = """from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BusinessProfile, Service, OperatingHour
from .forms import ServiceForm, OperatingHourForm

@login_required
def services_list(request):
    # Verificar que sea dueño
    if request.user.role != 'OWNER':
        return redirect('home')
    
    business = request.user.business_profile
    services = business.services.all()
    
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.business = business
            service.save()
            messages.success(request, '✅ Servicio agregado exitosamente.')
            return redirect('businesses:services')
    else:
        form = ServiceForm()

    return render(request, 'businesses/services.html', {'services': services, 'form': form})

@login_required
def schedule_list(request):
    if request.user.role != 'OWNER':
        return redirect('home')
        
    business = request.user.business_profile
    hours = business.operating_hours.all().order_by('day_of_week')
    
    if request.method == 'POST':
        form = OperatingHourForm(request.POST)
        if form.is_valid():
            # Evitar duplicados de día
            day = form.cleaned_data['day_of_week']
            OperatingHour.objects.filter(business=business, day_of_week=day).delete()
            
            hour = form.save(commit=False)
            hour.business = business
            hour.save()
            messages.success(request, '✅ Horario actualizado.')
            return redirect('businesses:schedule')
    else:
        form = OperatingHourForm()

    return render(request, 'businesses/schedule.html', {'hours': hours, 'form': form})
"""

# --- 3. URLS ---
urls_content = """from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('services/', views.services_list, name='services'),
    path('schedule/', views.schedule_list, name='schedule'),
]
"""

# --- 4. TEMPLATE: SERVICIOS ---
template_services = """{% extends 'businesses/base_dashboard.html' %}
{% block content %}
<div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="h3 fw-bold text-gray-800">🛠️ Mis Servicios</h2>
        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addServiceModal">
            <i class="fas fa-plus me-2"></i> Nuevo Servicio
        </button>
    </div>

    <div class="row">
        {% for service in services %}
        <div class="col-md-4 mb-4">
            <div class="card border-0 shadow-sm h-100 hover-scale">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <h5 class="fw-bold">{{ service.name }}</h5>
                        <span class="badge bg-success">${{ service.price }}</span>
                    </div>
                    <p class="text-muted small">{{ service.description|truncatechars:80 }}</p>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <small class="text-muted"><i class="far fa-clock"></i> {{ service.total_duration }} min</small>
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" {% if service.is_active %}checked{% endif %} disabled>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-12 text-center py-5">
            <p class="text-muted">Aún no has creado servicios.</p>
        </div>
        {% endfor %}
    </div>
</div>

<div class="modal fade" id="addServiceModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Agregar Nuevo Servicio</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="post">
                {% csrf_token %}
                <div class="modal-body">
                    {{ form.as_p }}
                </div>
                <div class="modal-footer">
                    <button type="submit" class="btn btn-primary w-100">Guardar Servicio</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
"""

# --- 5. TEMPLATE: HORARIOS ---
template_schedule = """{% extends 'businesses/base_dashboard.html' %}
{% block content %}
<div class="container-fluid py-4">
    <h2 class="h3 fw-bold text-gray-800 mb-4">📅 Horarios de Apertura</h2>
    
    <div class="row">
        <div class="col-md-4">
            <div class="card border-0 shadow-sm">
                <div class="card-body">
                    <h5 class="card-title mb-3">Configurar Día</h5>
                    <form method="post">
                        {% csrf_token %}
                        {{ form.as_p }}
                        <button type="submit" class="btn btn-dark w-100 mt-3">Guardar Horario</button>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="col-md-8">
            <div class="card border-0 shadow-sm">
                <div class="card-body p-0">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="bg-light">
                            <tr>
                                <th class="ps-4">Día</th>
                                <th>Apertura</th>
                                <th>Cierre</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for hour in hours %}
                            <tr>
                                <td class="ps-4 fw-bold">{{ hour.get_day_of_week_display }}</td>
                                {% if hour.is_closed %}
                                    <td colspan="2" class="text-muted">No laboral</td>
                                    <td><span class="badge bg-secondary">CERRADO</span></td>
                                {% else %}
                                    <td>{{ hour.opening_time|time:"H:i" }}</td>
                                    <td>{{ hour.closing_time|time:"H:i" }}</td>
                                    <td>
                                        {% if hour.crosses_midnight %}
                                            <span class="badge bg-indigo text-white" style="background-color: #6610f2;">🌙 AMANECIDA</span>
                                        {% else %}
                                            <span class="badge bg-success">NORMAL</span>
                                        {% endif %}
                                    </td>
                                {% endif %}
                            </tr>
                            {% empty %}
                            <tr><td colspan="4" class="text-center py-4">No has configurado horarios. El negocio aparecerá CERRADO siempre.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Archivo creado: {path}")

if __name__ == "__main__":
    print("🚀 Iniciando FASE 3: Servicios y Horarios...")
    
    write_file('apps/businesses/forms.py', forms_content)
    write_file('apps/businesses/views.py', views_content)
    write_file('apps/businesses/urls.py', urls_content)
    write_file('templates/businesses/services.html', template_services)
    write_file('templates/businesses/schedule.html', template_schedule)
    
    # Git Push
    try:
        print("🐙 Subiendo cambios a GitHub...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "feat: Phase 3 - Service & Schedule Management (Overnight logic)"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ ¡FASE 3 DESPLEGADA!")
    except Exception as e:
        print(f"⚠️ Error Git: {e}")
        
    try:
        os.remove(__file__)
    except:
        pass