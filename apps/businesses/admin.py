from django.contrib import admin
from .models import Salon, Service, Employee, Booking

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'whatsapp_number')
    search_fields = ('name', 'city')
    # Ya no incluimos ScheduleInline porque el modelo no existe
    inlines = [ServiceInline]

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'phone', 'is_active')
    list_filter = ('salon',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'salon', 'service', 'date_time', 'status')
    list_filter = ('status', 'date_time', 'salon')
