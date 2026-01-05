from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
    path('mis-citas/', views.client_dashboard, name='client_dashboard'),
]
