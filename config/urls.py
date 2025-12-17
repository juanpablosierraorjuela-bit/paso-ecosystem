from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from apps.users import views as user_views
from apps.businesses import views as biz_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # RUTAS PÚBLICAS
    path('', user_views.home, name='home'),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # DASHBOARD PRINCIPAL
    path('dashboard/', user_views.dashboard_view, name='dashboard'),
    path('dashboard/create-salon/', user_views.create_salon_view, name='create_salon'),
    path('dashboard/create-employee/', biz_views.create_employee_view, name='create_employee'),
    
    # GESTIÓN DE SERVICIOS (NUEVAS RUTAS)
    path('dashboard/services/', biz_views.manage_services_view, name='manage_services'),
    path('dashboard/services/add/', biz_views.add_service_view, name='add_service'),
    path('dashboard/services/edit/<int:service_id>/', biz_views.edit_service_view, name='edit_service'),
    path('dashboard/services/delete/<int:service_id>/', biz_views.delete_service_view, name='delete_service'),
    
    # CONFIGURACIONES
    path('dashboard/settings/', biz_views.salon_settings_view, name='salon_settings'),
    path('dashboard/employee/settings/', biz_views.employee_settings_view, name='employee_settings'),
    
    # PERFIL PÚBLICO
    path('salon/<slug:slug>/', biz_views.salon_detail, name='salon_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)