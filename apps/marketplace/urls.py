from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('salon/<int:pk>/', views.salon_detail, name='salon_detail'), # Pendiente siguiente paso
]