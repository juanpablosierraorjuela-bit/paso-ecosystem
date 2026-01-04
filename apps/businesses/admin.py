from django.contrib import admin
from .models import Salon, Service, Employee, Schedule, Booking

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0

class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 0

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'whatsapp_number')
    search_fields = ('name', 'city')
    inlines = [ServiceInline, ScheduleInline]

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'phone', 'is_active')
    list_filter = ('salon',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'salon', 'service', 'date_time', 'status')
    list_filter = ('status', 'date_time', 'salon')
