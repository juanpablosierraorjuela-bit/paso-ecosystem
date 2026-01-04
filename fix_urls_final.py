import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
URLS_PATH = os.path.join(APP_DIR, "urls.py")

# --- CONTENIDO DE URLS.PY SINCRONIZADO ---
CONTENIDO_URLS = """from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- PÚBLICO ---
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('salon/<int:salon_id>/', views.salon_detail, name='salon_detail'),
    path('negocios/', views.landing_businesses, name='landing_businesses'),

    # --- AUTENTICACIÓN ---
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # AQUI ESTABA EL ERROR: Ahora usamos RegisterOwnerView.as_view()
    path('accounts/register_owner/', views.RegisterOwnerView.as_view(), name='register_owner'),

    # --- MOTOR DE RESERVAS (WIZARD) ---
    path('reservar/<int:salon_id>/', views.booking_wizard, name='booking_wizard'),
    path('mi-cuenta/', views.client_dashboard, name='client_dashboard'),

    # --- REDIRECCIÓN INTELIGENTE ---
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),

    # --- PANEL DEL DUEÑO ---
    path('dashboard/owner/', views.OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('dashboard/settings/', views.OwnerSettingsView.as_view(), name='owner_settings'),

    # SERVICIOS
    path('dashboard/services/', views.OwnerServicesView.as_view(), name='owner_services'),
    path('dashboard/services/add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('dashboard/services/edit/<int:pk>/', views.ServiceUpdateView.as_view(), name='service_edit'),
    path('dashboard/services/delete/<int:pk>/', views.ServiceDeleteView.as_view(), name='service_delete'),

    # EMPLEADOS
    path('dashboard/employees/', views.OwnerEmployeesView.as_view(), name='owner_employees'),
    path('dashboard/employees/add/', views.EmployeeCreateView.as_view(), name='employee_add'),

    # --- PANEL DE EMPLEADO ---
    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),
]
"""

def arreglar_urls():
    print("🔗 Sincronizando urls.py con las nuevas vistas...")
    with open(URLS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_URLS)
    print("✅ ¡urls.py corregido! Ya no buscará funciones fantasmas.")

if __name__ == "__main__":
    arreglar_urls()