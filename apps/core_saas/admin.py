from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Columnas que verás en la lista
    list_display = ('username', 'email', 'role', 'phone', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username', 'phone')

    # Agregamos el campo 'role' y 'phone' al formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información Extra Paso', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Extra Paso', {'fields': ('role', 'phone')}),
    )