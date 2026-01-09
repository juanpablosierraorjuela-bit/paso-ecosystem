from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    # path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
]