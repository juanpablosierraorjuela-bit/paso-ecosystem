from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Registramos tu usuario personalizado para que aparezca en el panel
admin.site.register(User, UserAdmin)
