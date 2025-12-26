import os
import re
from pathlib import Path

# Ruta al archivo de modelos
BASE_DIR = Path(__file__).resolve().parent
MODELS_PATH = BASE_DIR / 'apps' / 'businesses' / 'models.py'

def mejorar_modelos():
    print(f"🧠 Mejorando inteligencia en: {MODELS_PATH}")
    
    with open(MODELS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. AGREGAR CAMPOS DE UBICACIÓN (Si no existen)
    # Buscamos donde termina la definición de campos básicos para insertar los nuevos
    if "city =" not in content:
        campos_nuevos = """    # --- UBICACIÓN REAL (Nivel Marketplace Nacional) ---
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección Física")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
"""
        # Insertamos después de 'name ='
        content = re.sub(r'(name = models.CharField\(.*?\))', r'\1\n' + campos_nuevos, content)
        print("   ✅ Campos de dirección y ciudad agregados.")

    # 2. INYECTAR LÓGICA DE HORARIOS INTELIGENTE
    # Esta función maneja zonas horarias y rangos complejos
    logica_apertura = """
    @property
    def is_open_now(self):
        \"\"\"Determina si el salón está abierto en este momento exacto.\"\"\"
        if not self.opening_time or not self.closing_time:
            return False
            
        from django.utils import timezone
        import datetime
        
        # Obtenemos la hora actual en la zona horaria del servidor (Colombia)
        now = timezone.localtime(timezone.now()).time()
        
        if self.opening_time < self.closing_time:
            # Horario normal (ej: 8am a 8pm)
            return self.opening_time <= now <= self.closing_time
        else:
            # Horario nocturno que cruza medianoche (ej: 6pm a 2am)
            return now >= self.opening_time or now <= self.closing_time
    """
    
    # Si ya existe is_open_now, no lo duplicamos, advertimos para reemplazar manual si es necesario
    if "def is_open_now(self):" not in content:
        # Lo insertamos antes del último __str__ o al final de la clase Salon
        content = re.sub(r'(def __str__\(self\):)', logica_apertura + r'\n    \1', content)
        print("   ✅ Lógica de horario inteligente inyectada.")
    else:
        print("   ℹ️ La lógica de horarios ya existía (verifica que sea la nueva versión).")

    # Guardar cambios
    with open(MODELS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    mejorar_modelos()
    print("\n⚠️ AHORA EJECUTA ESTOS COMANDOS MANUALMENTE:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. git add . && git commit -m 'Upgrade logica negocios' && git push")