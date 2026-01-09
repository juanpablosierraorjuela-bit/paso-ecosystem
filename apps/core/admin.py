from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, GlobalSettings

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'role', 'email', 'is_verified_payment', 'date_joined')
    list_filter = ('role', 'is_verified_payment')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos PASO', {'fields': ('role', 'phone', 'city', 'is_verified_payment', 'workplace')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(GlobalSettings)