from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Extra PASO', {'fields': ('role', 'phone', 'identification', 'address', 'avatar')}),
    )
