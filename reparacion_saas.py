import os

# DEFINIMOS EL MODELO CORRECTO (core_saas/models.py)
# Agregamos el campo 'salon' que faltaba en tu nuevo sistema
saas_model_content = """from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    '''
    Modelo de Usuario extendido para SaaS.
    Define quién es quién en la plataforma.
    '''
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Dueño / Administrador"
        EMPLOYEE = "EMPLOYEE", "Empleado / Barbero"
        CLIENT = "CLIENT", "Cliente Final"

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.CLIENT,
        verbose_name="Rol en la plataforma"
    )

    # Campos adicionales opcionales
    telefono = models.CharField(max_length=15, blank=True, null=True)
    
    # --- VINCULACIÓN CON EL SALÓN (CRÍTICO PARA QUE FUNCIONE EL DASHBOARD) ---
    # Esto permite que cada empleado pertenezca a un solo salón
    salon = models.ForeignKey(
        'businesses.Salon', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employees',
        verbose_name="Salón Asignado"
    )

    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
"""

def write_file(path, content):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Archivo Núcleo Actualizado: {path}")
    except Exception as e:
        print(f"❌ Error escribiendo {path}: {e}")

if __name__ == "__main__":
    print("🔧 Ajustando el motor core_saas...")
    write_file('core_saas/models.py', saas_model_content)
    print("\\n🚀 ¡Listo! Ahora sube los cambios a GitHub.")