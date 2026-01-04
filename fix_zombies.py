import os
import django
import sys
from django.db import transaction

# Configurar Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "paso_ecosystem.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.businesses.models import Salon

User = get_user_model()

print(" BUSCANDO USUARIOS ZOMBIS (Sin Negocio)...")

# 1. ELIMINAR USUARIOS ZOMBIS
# Buscamos usuarios con rol OWNER/ADMIN que NO tengan un Salón asociado
zombies = []
for user in User.objects.filter(role__in=["OWNER", "ADMIN"]):
    if not hasattr(user, "salon"):
        zombies.append(user)

if zombies:
    print(f" Encontrados {len(zombies)} usuarios corruptos. Eliminando...")
    for z in zombies:
        print(f"   - Eliminando usuario incompleto: {z.username} ({z.email})")
        z.delete()
    print(" Limpieza completada. Ya puedes re-usar esos nombres de usuario.")
else:
    print(" No se encontraron usuarios corruptos.")

# -----------------------------------------------------------------------------
# 2. ACTUALIZAR MODELS.PY (Core) - Alinear Rol OWNER
# -----------------------------------------------------------------------------
core_models_path = os.path.join("apps", "core_saas", "models.py")
print(f"\n Ajustando roles en {core_models_path}...")

new_core_models = r"""from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Actualizamos ADMIN por OWNER para que coincida con tus vistas
    ROLE_CHOICES = (("CLIENT", "Cliente"), ("OWNER", "Dueño de Negocio"), ("EMPLOYEE", "Empleado"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="CLIENT")
    phone = models.CharField(max_length=20, blank=True)

class PlatformSettings(models.Model):
    whatsapp_number = models.CharField(max_length=50, blank=True, help_text="Número WhatsApp del soporte")
    instagram_link = models.URLField(blank=True, help_text="Link completo de Instagram")
    
    class Meta:
        verbose_name = "Configuración de Plataforma"
        verbose_name_plural = "Configuración de Plataforma"

    def __str__(self):
        return "Ajustes Generales (Footer)"

    def save(self, *args, **kwargs):
        if not self.pk and PlatformSettings.objects.exists():
            return
        super().save(*args, **kwargs)
"""
with open(core_models_path, "w", encoding="utf-8") as f:
    f.write(new_core_models)

# -----------------------------------------------------------------------------
# 3. ACTUALIZAR VIEWS.PY (Agregar atomicidad para evitar futuros zombis)
# -----------------------------------------------------------------------------
views_path = os.path.join("apps", "businesses", "views.py")
print(f" Blindando registro en {views_path}...")

# Leemos el archivo actual y agregamos el import y el decorador
with open(views_path, "r", encoding="utf-8") as f:
    content = f.read()

# Agregamos el import de transaction si no está
if "from django.db import transaction" not in content:
    content = "from django.db import transaction\n" + content

# Decoramos la vista register_owner
if "@transaction.atomic" not in content:
    content = content.replace("def register_owner(request):", "@transaction.atomic\ndef register_owner(request):")

with open(views_path, "w", encoding="utf-8") as f:
    f.write(content)

# -----------------------------------------------------------------------------
# 4. SUBIR A GITHUB
# -----------------------------------------------------------------------------
import subprocess
print("\n Subiendo arreglos finales a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Eliminar usuarios zombis y blindar registro con atomic"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print(" ¡LISTO! Prueba registrarte de nuevo (puedes usar el mismo usuario).")
except Exception as e:
    print(f" Nota Git: {e}")

try:
    os.remove(__file__)
except:
    pass