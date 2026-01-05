from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_home, name='home'),
    path('negocio/<int:business_id>/', views.business_detail, name='business_detail'),
]
