from django.contrib import admin
from .models import Salon, Service, Employee, SalonSchedule

admin.site.register(Salon)
admin.site.register(Service)
admin.site.register(Employee)
admin.site.register(SalonSchedule)
