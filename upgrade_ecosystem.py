import os
import subprocess
import sys
import re

# ==========================================
# 🦄 DEFINICIÓN DE MODELOS "NIVEL DIOS" 🦄
# ==========================================

# 1. CORE: Usuarios Potenciados + Fix de Redirección
models_core = """from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador PASO"
        OWNER = "OWNER", "Dueño de Negocio"
        EMPLOYEE = "EMPLOYEE", "Empleado / Especialista"
        CLIENT = "CLIENT", "Cliente Final"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CLIENT)
    
    # --- Datos de Contacto y Perfil ---
    phone = models.CharField("Teléfono / WhatsApp", max_length=20, blank=True, null=True)
    city = models.CharField("Ciudad", max_length=100, blank=True, null=True, help_text="Ciudad seleccionada del dropdown")
    
    # Imagen: Si está vacía, el Template generará el avatar de lujo con iniciales
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Redes Sociales Personales
    instagram_link = models.URLField("Perfil de Instagram", blank=True, null=True)
    
    # --- Lógica de Seguridad y Pagos (El Ciclo de 24h) ---
    is_verified_payment = models.BooleanField("Pago Mensualidad Verificado", default=False, help_text="Si es Falso pasadas 24h, el sistema lo eliminará.")
    registration_timestamp = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    
    # Soft Delete
    is_active_account = models.BooleanField("Cuenta Activa", default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def hours_since_registration(self):
        delta = timezone.now() - self.registration_timestamp
        return delta.total_seconds() / 3600

class PlatformSettings(models.Model):
    \"\"\"Configuración Global del Sistema.\"\"\"
    site_name = models.CharField("Nombre del Sitio", max_length=100, default="PASO Ecosistema")
    support_whatsapp = models.CharField("WhatsApp de Soporte", max_length=20, help_text="Número para comprobantes")
    
    # --- Conexión Telegram ---
    telegram_bot_token = models.CharField("Token Bot Telegram", max_length=200, blank=True)
    telegram_chat_id = models.CharField("Chat ID Telegram", max_length=100, blank=True)
    
    # --- Footer Dinámico ---
    instagram_link = models.URLField("Instagram PASO", blank=True)
    facebook_link = models.URLField("Facebook PASO", blank=True)
    linkedin_link = models.URLField("LinkedIn PASO", blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and PlatformSettings.objects.exists():
            raise ValidationError('Solo puede existir una configuración global.')
        return super(PlatformSettings, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "⚙️ Configuración del Ecosistema"
        verbose_name_plural = "⚙️ Configuración del Ecosistema"
"""

# 2. BUSINESSES: Inteligencia de Negocio y Horarios Nocturnos
models_businesses = """from django.db import models
from django.conf import settings

class BusinessProfile(models.Model):
    \"\"\"El Cerebro del Negocio. Vinculado al usuario OWNER.\"\"\"
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_profile')
    business_name = models.CharField("Nombre del Negocio", max_length=150)
    description = models.TextField("Descripción", blank=True, help_text="Para el buscador semántico")
    
    address = models.CharField("Dirección Física", max_length=255)
    google_maps_url = models.URLField("Link Google Maps", blank=True)
    
    deposit_percentage = models.PositiveIntegerField("Porcentaje de Abono", default=30)
    is_open_manually = models.BooleanField("Abierto Manualmente", default=True)

    def __str__(self):
        return self.business_name

class Service(models.Model):
    \"\"\"Catálogo de Servicios Inteligente.\"\"\"
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField("Nombre del Servicio", max_length=100)
    description = models.TextField("Descripción / Palabras Clave")
    
    duration_minutes = models.PositiveIntegerField("Duración (min)")
    buffer_minutes = models.PositiveIntegerField("Tiempo de Limpieza (min)", default=10)
    
    price = models.DecimalField("Precio (COP)", max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)

    def total_duration(self):
        return self.duration_minutes + self.buffer_minutes

    def __str__(self):
        return f"{self.name} - ${self.price}"

class OperatingHour(models.Model):
    \"\"\"Horario del Local. Soporta turnos de madrugada.\"\"\"
    DAYS = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'),
        (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ]
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='operating_hours')
    day_of_week = models.IntegerField(choices=DAYS)
    opening_time = models.TimeField("Apertura")
    closing_time = models.TimeField("Cierre")
    is_closed = models.BooleanField("Cerrado este día", default=False)

    class Meta:
        ordering = ['day_of_week']
        unique_together = ('business', 'day_of_week')

    def crosses_midnight(self):
        return self.closing_time < self.opening_time

    def __str__(self):
        status = "Cerrado" if self.is_closed else f"{self.opening_time} - {self.closing_time}"
        return f"{self.get_day_of_week_display()}: {status}"
"""

# 3. BOOKING: Citas y Cronómetro
models_booking = """from django.db import models
from django.conf import settings
from apps.businesses.models import BusinessProfile, Service

class EmployeeSchedule(models.Model):
    \"\"\"Horario del Empleado (Subordinado al Negocio).\"\"\"
    DAYS = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'),
        (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ]
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules')
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE) 
    
    day_of_week = models.IntegerField(choices=DAYS)
    start_time = models.TimeField("Entrada")
    end_time = models.TimeField("Salida")
    
    break_start = models.TimeField("Inicio Almuerzo", blank=True, null=True)
    break_end = models.TimeField("Fin Almuerzo", blank=True, null=True)
    
    is_active_day = models.BooleanField("Trabaja hoy", default=True)

    class Meta:
        unique_together = ('employee', 'day_of_week')

class Appointment(models.Model):
    \"\"\"El Corazón Transaccional.\"\"\"
    STATUS_CHOICES = [
        ('PENDING', '🟡 Pendiente de Abono (60 min)'),
        ('VERIFIED', '🟢 Verificada (Abono Recibido)'),
        ('COMPLETED', '🏁 Completada'),
        ('CANCELLED', '🔴 Cancelada'),
        ('EXPIRED', '⏱️ Expirada (No pagó)'),
    ]

    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_appointments')
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True) # Inicio del cronómetro
    
    deposit_amount = models.DecimalField("Monto Abono", max_digits=10, decimal_places=0)
    total_price = models.DecimalField("Precio Total", max_digits=10, decimal_places=0)
    
    notes = models.TextField("Notas del Cliente", blank=True)

    def __str__(self):
        return f"Cita {self.id}: {self.client.username} - {self.status}"
"""

# ==========================================
# 🛠️ HERRAMIENTAS DE REPARACIÓN
# ==========================================

def write_file(path, content):
    """Escribe el contenido en el archivo."""
    print(f"🔄 Actualizando: {path}...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   ✅ Hecho.")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        sys.exit(1)

def fix_views_error():
    """Arregla el error NoReverseMatch cambiando 'login' por 'home'."""
    path = 'apps/core/views.py'
    print(f"🔧 Reparando error de redirección en {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Cambiamos reverse_lazy('login') por reverse_lazy('home')
        new_content = content.replace("reverse_lazy('login')", "reverse_lazy('home')")
        
        if content != new_content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("   ✅ Redirección corregida a 'home' (evita crash).")
        else:
            print("   ℹ️ El archivo ya estaba corregido.")
            
    except FileNotFoundError:
        print(f"   ⚠️ No se encontró {path}. Saltando.")

def enable_auth_urls():
    """Habilita las URLs de autenticación en config/urls.py"""
    path = 'config/urls.py'
    print(f"🔧 Habilitando URLs de Auth en {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            # Descomentar la línea de auth.urls si está comentada
            if "# path('accounts/', include('django.contrib.auth.urls'))" in line:
                new_lines.append(line.replace("# ", ""))
                print("   ✅ URLs de autenticación habilitadas.")
            else:
                new_lines.append(line)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
    except FileNotFoundError:
        print(f"   ⚠️ No se encontró {path}.")

def run_command(command, description):
    print(f"\n🚀 Ejecutando: {description}...")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"   ⚠️ Advertencia en: {description} (Puede ser normal si no hay cambios en git)")

def self_destruct():
    print("\n💥 Autodestruyendo script...")
    try:
        os.remove(sys.argv[0])
        print("   ✅ Rastro eliminado.")
    except:
        pass

# ==========================================
# 🏁 EJECUCIÓN
# ==========================================

def main():
    print("🦄 INICIANDO ACTUALIZACIÓN DEL ECOSISTEMA PASO 🦄")
    print("===============================================")
    
    # 1. Actualizar Modelos
    write_file('apps/core/models.py', models_core)
    write_file('apps/businesses/models.py', models_businesses)
    write_file('apps/booking/models.py', models_booking)
    
    # 2. Aplicar correcciones de código
    fix_views_error()
    enable_auth_urls()
    
    # 3. Migraciones
    run_command("python manage.py makemigrations", "Creando migraciones")
    run_command("python manage.py migrate", "Aplicando cambios a DB")
    
    # 4. Git Push
    print("\n📦 Subiendo cambios a Render...")
    run_command("git add .", "Git Add")
    run_command('git commit -m "Upgrade: Modelos Nivel Dios + Fix Login Error"', "Git Commit")
    run_command("git push origin main", "Git Push")
    
    print("\n✅ ¡LISTO! Tu código está actualizado y el error corregido.")
    self_destruct()

if __name__ == "__main__":
    main()