from django.contrib import admin
from .models import Salon, Service, Booking, EmployeeSchedule

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    # HEMOS QUITADO 'phone' DE AQUÍ PARA EVITAR EL ERROR
    list_display = ('name', 'is_active', 'opening_time', 'closing_time')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(EmployeeSchedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('employee', 'weekday', 'from_hour', 'to_hour')
    list_filter = ('weekday', 'employee')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'price', 'duration_minutes')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'service', 'employee', 'start_time', 'status')
    list_filter = ('status', 'start_time')
