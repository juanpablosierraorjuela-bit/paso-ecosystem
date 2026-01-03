import os
import sys

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates", "dashboard")

VIEWS_PATH = os.path.join(APP_DIR, "views.py")
URLS_PATH = os.path.join(APP_DIR, "urls.py")
FORMS_PATH = os.path.join(APP_DIR, "forms.py")
SERVICES_HTML = os.path.join(TEMPLATES_DIR, "owner_services.html")
SERVICE_FORM_HTML = os.path.join(TEMPLATES_DIR, "service_form.html") # Nuevo archivo para el formulario

# --- 1. MEJORAR EL FORMULARIO (forms.py) ---
def mejorar_forms():
    print("📝 1. Mejorando formulario de Servicios...")
    with open(FORMS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Reemplazamos la clase ServiceForm básica por una estilizada
    if "class ServiceForm(forms.ModelForm):" in content:
        # Definición vieja vs nueva
        nuevo_form = """
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
"""
        # Buscamos y reemplazamos la clase simple
        import re
        patron = r"class ServiceForm\(forms\.ModelForm\):[\s\S]*?fields = '__all__'"
        
        # Si la encontramos simple, la reemplazamos. Si ya es compleja, la dejamos.
        if "fields = '__all__'" in content:
            content = re.sub(patron, nuevo_form.strip(), content)
            with open(FORMS_PATH, "w", encoding="utf-8") as f:
                f.write(content)
            print("   -> ServiceForm actualizado con estilos.")
        else:
            print("   -> ServiceForm ya estaba estilizado.")

# --- 2. AGREGAR LOGICA DE CREAR/EDITAR (views.py) ---
def actualizar_views():
    print("🧠 2. Agregando lógica para Crear, Editar y Borrar...")
    with open(VIEWS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Inyección de las nuevas vistas
    nuevas_vistas = """

# --- GESTIÓN DE SERVICIOS (Agregado por activador_servicios.py) ---
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')

    def form_valid(self, form):
        service = form.save(commit=False)
        service.salon = self.request.user.salon  # Asigna el servicio al salón del dueño
        service.save()
        return super().form_valid(form)

class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')

    def get_queryset(self):
        # Seguridad: Solo editar servicios propios
        return Service.objects.filter(salon__owner=self.request.user)

class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'dashboard/service_confirm_delete.html'
    success_url = reverse_lazy('owner_services')

    def get_queryset(self):
        # Seguridad: Solo borrar servicios propios
        return Service.objects.filter(salon__owner=self.request.user)
"""
    if "class ServiceCreateView" not in content:
        with open(VIEWS_PATH, "a", encoding="utf-8") as f:
            f.write(nuevas_vistas)
        print("   -> Vistas de Servicios agregadas al final de views.py.")
    else:
        print("   -> Las vistas ya existían.")

# --- 3. CONECTAR URLS (urls.py) ---
def actualizar_urls():
    print("🔗 3. Conectando las URLs...")
    with open(URLS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    rutas_nuevas = [
        "    path('dashboard/services/add/', views.ServiceCreateView.as_view(), name='service_add'),",
        "    path('dashboard/services/edit/<int:pk>/', views.ServiceUpdateView.as_view(), name='service_edit'),",
        "    path('dashboard/services/delete/<int:pk>/', views.ServiceDeleteView.as_view(), name='service_delete'),"
    ]
    
    # Insertar antes del cierre de urlpatterns
    if "service_add" not in content:
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if "]" in line: # Encontrar el cierre de la lista
                # Insertar justo antes
                lines.insert(i, "\n".join(rutas_nuevas))
                break
        
        with open(URLS_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("   -> URLs de servicios conectadas.")
    else:
        print("   -> URLs ya existían.")

# --- 4. ACTUALIZAR HTML (owner_services.html y service_form.html) ---
def actualizar_templates():
    print("🎨 4. Creando interfaz de Servicios...")
    
    # A. La tabla principal (owner_services.html)
    html_tabla = """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold text-dark">Mis Servicios</h2>
        <a href="{% url 'service_add' %}" class="btn btn-dark">
            <i class="bi bi-plus-lg"></i> Nuevo Servicio
        </a>
    </div>

    <div class="card shadow-sm border-0">
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="bg-light">
                        <tr>
                            <th class="ps-4">Nombre</th>
                            <th>Duración</th>
                            <th>Precio</th>
                            <th class="text-end pe-4">Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for service in services %}
                        <tr>
                            <td class="ps-4 fw-bold">{{ service.name }}</td>
                            <td>{{ service.duration_minutes }} min</td>
                            <td>${{ service.price }}</td>
                            <td class="text-end pe-4">
                                <a href="{% url 'service_edit' service.pk %}" class="btn btn-sm btn-outline-dark me-1">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                <a href="{% url 'service_delete' service.pk %}" class="btn btn-sm btn-outline-danger">
                                    <i class="bi bi-trash"></i>
                                </a>
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="4" class="text-center py-5 text-muted">
                                <i class="bi bi-scissors display-4 d-block mb-3"></i>
                                No tienes servicios registrados aún.<br>
                                ¡Agrega el primero para que tus clientes reserven!
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="mt-4">
        <a href="{% url 'owner_dashboard' %}" class="text-muted text-decoration-none">
            <i class="bi bi-arrow-left"></i> Volver al Panel
        </a>
    </div>
</div>
{% endblock %}
"""
    with open(SERVICES_HTML, "w", encoding="utf-8") as f:
        f.write(html_tabla)

    # B. El formulario para crear/editar (service_form.html)
    html_form = """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-white border-bottom">
                    <h4 class="mb-0 fw-bold">
                        {% if object %}Editar Servicio{% else %}Nuevo Servicio{% endif %}
                    </h4>
                </div>
                <div class="card-body p-4">
                    <form method="post">
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label class="form-label fw-bold">Nombre del Servicio</label>
                            {{ form.name }}
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label fw-bold">Descripción (Opcional)</label>
                            {{ form.description }}
                        </div>

                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">Duración (Min)</label>
                                {{ form.duration_minutes }}
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">Precio ($)</label>
                                {{ form.price }}
                            </div>
                        </div>

                        <div class="d-grid gap-2 mt-4">
                            <button type="submit" class="btn btn-dark btn-lg">Guardar Servicio</button>
                            <a href="{% url 'owner_services' %}" class="btn btn-outline-secondary">Cancelar</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    with open(SERVICE_FORM_HTML, "w", encoding="utf-8") as f:
        f.write(html_form)
        
    # C. Confirmación de borrado
    confirm_delete_html = os.path.join(TEMPLATES_DIR, "service_confirm_delete.html")
    html_delete = """{% extends 'base.html' %}
{% block content %}
<div class="container py-5 text-center">
    <div class="card shadow-sm border-0 d-inline-block text-start" style="max-width: 500px;">
        <div class="card-body p-5">
            <h3 class="text-danger mb-3">¿Eliminar Servicio?</h3>
            <p>Vas a eliminar <strong>"{{ object.name }}"</strong>. Esta acción no se puede deshacer.</p>
            <form method="post">
                {% csrf_token %}
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-danger">Sí, eliminar</button>
                    <a href="{% url 'owner_services' %}" class="btn btn-outline-secondary">Cancelar</a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
"""
    with open(confirm_delete_html, "w", encoding="utf-8") as f:
        f.write(html_delete)
        
    print("   -> Templates creados: Lista, Formulario y Confirmación de borrado.")

if __name__ == "__main__":
    print("🚀 ACTIVANDO GESTIÓN DE SERVICIOS...")
    mejorar_forms()
    actualizar_views()
    actualizar_urls()
    actualizar_templates()
    print("\n✅ LISTO. Ahora puedes agregar servicios en tu panel.")