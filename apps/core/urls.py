from django.urls import path
from .views import LandingPageView, OwnerRegisterView

urlpatterns = [
    path('', LandingPageView.as_view(), name='home'),
    path('registro-negocio/', OwnerRegisterView.as_view(), name='register_owner'),
]
