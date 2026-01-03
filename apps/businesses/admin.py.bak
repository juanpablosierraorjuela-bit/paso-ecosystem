from django.contrib import admin
from .models import Salon, Service, Employee, Booking, Schedule

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0

class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 0

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'owner_email')
    search_fields = ('name', 'city', 'owner__email')
    inlines = [ServiceInline, EmployeeInline]

    def owner_email(self, obj):
        return obj.owner.email

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'salon', 'service', 'date_time', 'status')
    list_filter = ('status', 'date_time', 'salon')
