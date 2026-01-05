from django.urls import path
from .views import home, OwnerRegisterView, dashboard_redirect, pain_landing

urlpatterns = [
    path('', home, name='home'),
    path('soluciones-negocios/', pain_landing, name='pain_landing'), # URL Marketing
    path('registro-negocio/', OwnerRegisterView.as_view(), name='register_owner'),
    path('dashboard/', dashboard_redirect, name='dashboard'),
]
