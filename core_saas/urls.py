from django.urls import path
from .views import (
    SaasLoginView, OwnerSignupView, ClientSignupView, 
    CreateSalonView, AdminDashboardView, EmployeePanelView,
    CreateEmployeeView
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Auth
    path('login/', SaasLoginView.as_view(), name='saas_login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    
    # Registros Separados
    path('registro-negocio/', OwnerSignupView.as_view(), name='registro_owner'),
    path('registro-cliente/', ClientSignupView.as_view(), name='registro_cliente'),

    # Flujo Dueño
    path('crear-mi-salon/', CreateSalonView.as_view(), name='crear_salon'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('crear-empleado/', CreateEmployeeView.as_view(), name='crear_empleado'),

    # Flujo Empleado
    path('employee-panel/', EmployeePanelView.as_view(), name='employee_panel'),
]
