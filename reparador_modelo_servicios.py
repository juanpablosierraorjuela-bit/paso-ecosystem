import os
import sys

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_PATH = os.path.join(BASE_DIR, "apps", "businesses", "models.py")

def arreglar_modelo_service():
    print("🔧 Reparando modelo Service en models.py...")
    
    with open(MODELS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Verificamos si ya tiene duration_minutes
    if "duration_minutes =" in content:
        print("   -> El campo duration_minutes ya existe. No se toca nada.")
        return

    # Si no existe, buscamos la clase Service y lo inyectamos
    # Buscamos "class Service(models.Model):"
    if "class Service(models.Model):" in content:
        # Definimos el campo nuevo
        nuevo_campo = "\n    duration_minutes = models.IntegerField(default=30, verbose_name='Duración (min)')"
        
        # Reemplazamos la definición de la clase para insertar el campo justo después
        new_content = content.replace(
            "class Service(models.Model):", 
            "class Service(models.Model):" + nuevo_campo
        )
        
        with open(MODELS_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("   -> Campo 'duration_minutes' agregado exitosamente al modelo Service.")
    else:
        print("❌ Error: No encontré la clase Service en models.py")

if __name__ == "__main__":
    arreglar_modelo_service()