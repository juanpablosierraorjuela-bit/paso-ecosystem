from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('panel/', views.owner_dashboard, name='dashboard'),
    path('servicios/', views.services_list, name='services'),
    path('equipo/', views.employees_list, name='employees'),
    path('horario/', views.schedule_config, name='schedule'),
    path('configuracion/', views.business_settings, name='settings'),
]
