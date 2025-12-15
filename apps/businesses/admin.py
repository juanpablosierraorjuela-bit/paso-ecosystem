from django.contrib import admin
from .models import Salon, Service, Booking, OpeningHours, Employee

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'owner')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'price', 'duration_minutes')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Cambiamos Appointment por Booking
    list_display = ('customer_name', 'service', 'start_time', 'employee', 'status')
    list_filter = ('status', 'start_time')

@admin.register(OpeningHours)
class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = ('salon', 'get_weekday_display', 'from_hour', 'to_hour', 'is_closed')
    list_filter = ('salon',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'user')
    def name(self, obj):
        return obj.user.get_full_name()