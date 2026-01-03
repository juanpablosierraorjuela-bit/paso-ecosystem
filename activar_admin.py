import os
import textwrap
import subprocess
import sys

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory: os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"✅ Panel de Control Activado: {path}")

print("👑 ACTIVANDO MODO DIOS EN EL ADMIN DE DJANGO...")

# ==============================================================================
# 1. ADMIN DE NEGOCIOS (Super completo)
# ==============================================================================
admin_business_content = """
from django.contrib import admin
from .models import Salon, Service, Employee, Booking, Schedule, OpeningHours

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'owner', 'phone', 'deposit_percentage', 'created_at')
    list_filter = ('city', 'created_at')
    search_fields = ('name', 'owner__email', 'owner__username', 'phone')
    ordering = ('-created_at',)
    list_per_page = 20

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'salon', 'service', 'date', 'time', 'status_colored')
    list_filter = ('status', 'date', 'salon')
    search_fields = ('customer_name', 'customer_email', 'salon__name')
    date_hierarchy = 'date'
    
    # Colores para los estados
    from django.utils.html import format_html
    def status_colored(self, obj):
        colors = {
            'pending_payment': 'orange',
            'confirmed': 'green',
            'cancelled': 'red',
            'expired': 'gray',
            'in_review': 'blue',
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())
    status_colored.short_description = 'Estado'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'price', 'duration_minutes')
    list_filter = ('salon',)
    search_fields = ('name', 'salon__name')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'is_active')
    list_filter = ('salon', 'is_active')

# Registros simples para horarios
admin.site.register(Schedule)
admin.site.register(OpeningHours)
"""
create_file('apps/businesses/admin.py', admin_business_content)

# ==============================================================================
# 2. ADMIN DE USUARIOS (Para ver quién es Dueño y quién Cliente)
# ==============================================================================
admin_users_content = """
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
"""
create_file('apps/core_saas/admin.py', admin_users_content)

# ==============================================================================
# 3. SUBIDA AUTOMÁTICA
# ==============================================================================
print("🤖 Subiendo configuración de Admin a Render...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Admin: Enable full dashboard for Superuser"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🚀 ¡HECHO! Espera 2 minutos a que Render actualice.")
    print("   Luego entra a /admin y verás TODO tu imperio.")
except Exception as e:
    print(f"⚠️ Error git: {e}")

print("💥 Autodestruyendo script de configuración...")
try:
    os.remove(__file__)
except: pass