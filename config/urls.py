from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core_saas.urls')),
    path('negocio/', include('apps.businesses.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
]