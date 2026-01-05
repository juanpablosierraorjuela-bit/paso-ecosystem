from django.urls import path
from .views import home, OwnerRegisterView, dashboard_redirect

urlpatterns = [
    path('', home, name='home'),
    path('registro-negocio/', OwnerRegisterView.as_view(), name='register_owner'),
    path('dashboard/', dashboard_redirect, name='dashboard'),
]
