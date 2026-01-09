from django.urls import path
from . import views

urlpatterns = [
    path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    path('servicios/', views.services_list, name='services_list'),
    path('servicios/borrar/<int:pk>/', views.service_delete, name='service_delete'),
    path('equipo/', views.employees_list, name='employees_list'),
    path('equipo/borrar/<int:pk>/', views.employee_delete, name='employee_delete'),
    path('configuracion/', views.settings_view, name='settings_view'),
]