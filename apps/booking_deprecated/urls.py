from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
    path('mi-horario/', views.employee_schedule, name='employee_schedule'),
    path('mi-perfil/', views.employee_profile, name='employee_profile'),
    path('mis-citas/', views.client_dashboard, name='client_dashboard'),
]
