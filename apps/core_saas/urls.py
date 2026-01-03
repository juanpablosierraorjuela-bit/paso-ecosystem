from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='saas_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='saas_logout'),
]
