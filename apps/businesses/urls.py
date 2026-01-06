
from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('dashboard/', views.owner_dashboard, name='dashboard'),
]
