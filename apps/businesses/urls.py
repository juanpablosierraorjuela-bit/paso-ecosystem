from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    # Panel Principal
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    
    # Gestión (Sub-rutas necesarias para que el dashboard funcione)
    path('servicios/', views.services_list, name='services'),
    path('servicios/eliminar/<int:pk>/', views.service_delete, name='service_delete'),
    
    path('equipo/', views.employees_list, name='employees'),
    
    path('configuracion/', views.settings_view, name='settings'),
]