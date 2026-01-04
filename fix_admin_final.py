import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
ADMIN_PATH = os.path.join(APP_DIR, "admin.py")

# --- CONTENIDO CORRECTO DE ADMIN.PY ---
CONTENIDO_ADMIN = """from django.contrib import admin
from .models import Salon, Service, Employee, SalonSchedule, EmployeeSchedule, Booking

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    # Campos actuales: name, owner, city, whatsapp
    list_display = ('name', 'owner', 'city', 'whatsapp')
    search_fields = ('name', 'owner__email', 'city')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    # Campos actuales: name, salon, price, duration_minutes
    list_display = ('name', 'salon', 'price', 'duration_minutes')
    list_filter = ('salon',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # Campos actuales: first_name, last_name, salon
    list_display = ('first_name', 'last_name', 'salon', 'phone')
    list_filter = ('salon',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Campos actuales: customer, salon, employee, date, time, status
    list_display = ('customer', 'salon', 'employee', 'date', 'time', 'status')
    list_filter = ('status', 'date', 'salon')
    search_fields = ('customer__username', 'customer__email')

# Registros simples para horarios
admin.site.register(SalonSchedule)
admin.site.register(EmployeeSchedule)
"""

def arreglar_admin():
    print("🛠️ Reparando admin.py para eliminar campos viejos...")
    with open(ADMIN_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_ADMIN)
    print("✅ ¡admin.py sincronizado con la base de datos!")

if __name__ == "__main__":
    arreglar_admin()