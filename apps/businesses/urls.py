from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('services/', views.services_list, name='services'),
    path('schedule/', views.schedule_list, name='schedule'),
    # RUTAS NUEVAS AGREGADAS POR EL SCRIPT MÁGICO
    path('panel/', views.panel_negocio, name='panel_negocio'),
]
