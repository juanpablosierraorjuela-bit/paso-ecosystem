import os
import subprocess
import sys
import time

# ==========================================
# 🦄 DEFINICIÓN DE MODELOS "NIVEL DIOS" 🦄
# ==========================================

# 1. CORE: Usuarios, Configuración Global y Lógica de Verificación
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
    city = models.CharField("Ciudad", max_length=100, blank=True, null=True, help_text="Ciudad seleccionada del dropdown de 1101 municipios")
    
    # Imagen: Si está vacía, el Template generará el avatar de lujo con iniciales
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Redes Sociales Personales (Para empleados o dueños)
    instagram_link = models.URLField("Perfil de Instagram", blank=True, null=True)
    
    # --- Lógica de Seguridad y Pagos (El Ciclo de 24h) ---
    is_verified_payment = models.BooleanField("Pago Mensualidad Verificado", default=False, help_text="Si es Falso pasadas 24h, el sistema lo eliminará.")
    registration_timestamp = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    
    # Soft Delete: En lugar de borrar directo, marcamos como inactivo antes de la purga final
    is_active_account = models.BooleanField("Cuenta Activa", default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def hours_since_registration(self):
        delta = timezone.now() - self.registration_timestamp
        return delta.total_seconds() / 3600

class PlatformSettings(models.Model):
    \"\"\"
    Configuración Global del Sistema controlada por el Superusuario.
    \"\"\"
    site_name = models.CharField("Nombre del Sitio", max_length=100, default="PASO Ecosistema")
    support_whatsapp = models.CharField("WhatsApp de Soporte", max_length=20, help_text="Número donde los dueños envían comprobantes")
    
    # --- Conexión Telegram ---
    telegram_bot_token = models.CharField("Token Bot Telegram", max_length=200, blank=True)
    telegram_chat_id = models.CharField("Chat ID Telegram", max_length=100, blank=True)
    
    # --- Footer Dinámico ---
    instagram_link = models.URLField("Instagram PASO", blank=True)
    facebook_link = models.URLField("Facebook PASO", blank=True)
    linkedin_link = models.URLField("LinkedIn PASO", blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and PlatformSettings.objects.exists():
            raise ValidationError('Solo puede existir una configuración global del ecosistema.')
        return super(PlatformSettings, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "⚙️ Configuración del Ecosistema"
        verbose_name_plural = "⚙️ Configuración del Ecosistema"
"""

# 2. BUSINESSES: Perfil del Negocio, Horarios Nocturnos y Servicios
models_businesses = """from django.db import models
from django.conf import settings

class BusinessProfile(models.Model):
    \"\"\"
    El Cerebro del Negocio. Vinculado al usuario OWNER.
    \"\"\"
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_profile')
    business_name = models.CharField("Nombre del Negocio", max_length=150)
    description = models.TextField("Descripción", blank=True, help_text="Texto persuasivo para el buscador semántico")
    
    # --- Ubicación ---
    address = models.CharField("Dirección Física", max_length=255)
    google_maps_url = models.URLField("Link Google Maps", blank=True, help_text="Para el botón flotante en la tarjeta")
    
    # --- Configuración Financiera ---
    deposit_percentage = models.PositiveIntegerField("Porcentaje de Abono", default=30, help_text="Porcentaje (0-100) requerido para reservar")
    
    # --- Interruptores de Estado ---
    is_open_manually = models.BooleanField("Abierto Manualmente", default=True, help_text="Switch de emergencia para cerrar el negocio en el Marketplace")

    def __str__(self):
        return self.business_name

class Service(models.Model):
    \"\"\"
    Catálogo de Servicios Inteligente.
    \"\"\"
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField("Nombre del Servicio", max_length=100)
    description = models.TextField("Descripción / Palabras Clave", help_text="Descripción para búsqueda semántica (Ej: 'Ideal para cabello seco')")
    
    # --- Tiempos ---
    duration_minutes = models.PositiveIntegerField("Duración del Servicio (min)")
    buffer_minutes = models.PositiveIntegerField("Tiempo de Limpieza/Buffer (min)", default=10, help_text="Tiempo muerto entre citas para organizar")
    
    price = models.DecimalField("Precio (COP)", max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)

    def total_duration(self):
        return self.duration_minutes + self.buffer_minutes

    def __str__(self):
        return f"{self.name} - ${self.price}"

class OperatingHour(models.Model):
    \"\"\"
    Capa 1 de Disponibilidad: Horario del Local.
    Soporta 'Overnight Shift' (Ej: Abre Sábado 10PM -> Cierra Domingo 5AM).
    \"\"\"
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
        \"\"\"Devuelve True si el turno termina al día siguiente\"\"\"
        return self.closing_time < self.opening_time

    def __str__(self):
        status = "Cerrado" if self.is_closed else f"{self.opening_time} - {self.closing_time}"
        return f"{self.get_day_of_week_display()}: {status}"
"""

# 3. BOOKING: Citas, Empleados y Lógica de Abonos
models_booking = """from django.db import models
from django.conf import settings
from apps.businesses.models import BusinessProfile, Service

class EmployeeSchedule(models.Model):
    \"\"\"
    Capa 2 de Disponibilidad: Horario del Empleado.
    Subordinado al horario del negocio.
    \"\"\"
    DAYS = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'),
        (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ]
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules')
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE) 
    
    day_of_week = models.IntegerField(choices=DAYS)
    start_time = models.TimeField("Entrada")
    end_time = models.TimeField("Salida")
    
    # --- Descansos ---
    break_start = models.TimeField("Inicio Almuerzo", blank=True, null=True)
    break_end = models.TimeField("Fin Almuerzo", blank=True, null=True)
    
    # --- Switch de Emergencia ---
    is_active_day = models.BooleanField("Trabaja hoy", default=True, help_text="Desactivar si el empleado faltó hoy")

    class Meta:
        unique_together = ('employee', 'day_of_week')

class Appointment(models.Model):
    \"\"\"
    El Corazón Transaccional.
    Maneja el estado PENDING para el cronómetro de 60 minutos.
    \"\"\"
    STATUS_CHOICES = [
        ('PENDING', '🟡 Pendiente de Abono (60 min)'),
        ('VERIFIED', '🟢 Verificada (Abono Recibido)'),
        ('COMPLETED', '🏁 Completada'),
        ('CANCELLED', '🔴 Cancelada'),
        ('EXPIRED', '⏱️ Expirada (No pagó)'),
    ]

    # Relaciones
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_appointments')
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    # Tiempo
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Estado y Pagos
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True) # Inicio del cronómetro de 60 min
    
    deposit_amount = models.DecimalField("Monto Abono", max_digits=10, decimal_places=0)
    total_price = models.DecimalField("Precio Total", max_digits=10, decimal_places=0)
    
    notes = models.TextField("Notas del Cliente", blank=True)

    def __str__(self):
        return f"Cita {self.id}: {self.client.username} - {self.status}"
"""

# ==========================================
# 🛠️ FUNCIONES DEL SISTEMA
# ==========================================

def write_file(path, content):
    """Escribe el contenido en el archivo, creando carpetas si faltan."""
    print(f"🔄 Procesando: {path}...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   ✅ Archivo actualizado.")
    except Exception as e:
        print(f"   ❌ Error crítico escribiendo {path}: {e}")
        sys.exit(1)

def run_command(command, description):
    """Ejecuta comandos de terminal y maneja errores."""
    print(f"\n🚀 Ejecutando: {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(f"   ✅ Éxito.")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Falló: {e.stderr}")
        # No salimos con exit(1) en git push para evitar bloquear si no hay cambios, pero avisamos.
        if "git" in command:
            print("      (Si el error es 'nothing to commit', puedes ignorarlo).")
        else:
            sys.exit(1)

def self_destruct():
    """Borra este script al finalizar."""
    print("\n💥 Iniciando secuencia de autodestrucción del script...")
    try:
        os.remove(sys.argv[0])
        print("   ✅ Script eliminado. Rastro borrado.")
    except Exception as e:
        print(f"   ⚠️ No se pudo autodestruir: {e}")

# ==========================================
# 🏁 EJECUCIÓN PRINCIPAL
# ==========================================

def main():
    print("🦄 INICIANDO PROTOCOLO: ACTUALIZACIÓN ECOSISTEMA PASO 🦄")
    print("=========================================================")
    
    # 1. Inyectar Modelos
    write_file('apps/core/models.py', models_core)
    write_file('apps/businesses/models.py', models_businesses)
    write_file('apps/booking/models.py', models_booking)
    
    # 2. Reconstruir Base de Datos Local
    run_command("python manage.py makemigrations", "Creando nuevas migraciones")
    run_command("python manage.py migrate", "Aplicando estructura a la DB Local")
    
    # 3. Despliegue a la Nube
    print("\n☁️ Preparando subida a Render...")
    run_command("git add .", "Añadiendo archivos al stage")
    run_command('git commit -m "Upgrade: Modelos Nivel Dios (Usuarios, Negocios, Citas)"', "Creando Commit")
    run_command("git push origin main", "Enviando código a GitHub/Render")
    
    print("\n✅ ¡Misión Cumplida! Tu Ecosistema se está actualizando en la nube.")
    
    # 4. Autodestrucción
    self_destruct()

if __name__ == "__main__":
    main()