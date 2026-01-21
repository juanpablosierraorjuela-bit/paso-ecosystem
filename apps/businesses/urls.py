from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.owner_dashboard, name='dashboard') if hasattr(views, 'owner_dashboard') else path('temp/', lambda r: None),
    path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
    path('configuracion/', views.settings_view, name='settings_view') if hasattr(views, 'settings_view') else path('temp2/', lambda r: None),
    # ... resto de tus rutas
]
