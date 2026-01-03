from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Salon(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    instagram_link = models.URLField(blank=True, null=True)
    deposit_percentage = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name) + '-' + str(self.owner.id)[:4]
        super().save(*args, **kwargs)

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    duration_minutes = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

class Schedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time = models.TimeField(default='09:00')
    end_time = models.TimeField(default='18:00')
    is_active = models.BooleanField(default=True)
    lunch_start = models.TimeField(null=True, blank=True)
    lunch_end = models.TimeField(null=True, blank=True)

class OpeningHours(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time = models.TimeField(default='08:00')
    end_time = models.TimeField(default='20:00')
    is_closed = models.BooleanField(default=False)

class Booking(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default='pending_payment')
    created_at = models.DateTimeField(auto_now_add=True)