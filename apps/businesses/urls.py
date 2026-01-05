from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('panel/', views.owner_dashboard, name='dashboard'),
]
