from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro-dueno/', views.register_owner, name='register_owner'),
    path('login/', views.login_view, name='login'),
]