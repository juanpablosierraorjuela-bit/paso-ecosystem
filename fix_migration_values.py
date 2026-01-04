import os
import glob

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MIGRATIONS_DIR = os.path.join(BASE_DIR, "apps", "businesses", "migrations")

def arreglar_migracion_0003():
    print("🩺 Buscando archivo de migración 0003...")
    
    # Buscar cualquier archivo que empiece con 0003 en la carpeta de migraciones
    archivos = glob.glob(os.path.join(MIGRATIONS_DIR, "0003_*.py"))
    
    if not archivos:
        print("❌ No encontré la migración 0003. Verifica que exista.")
        return

    archivo_migracion = archivos[0]
    print(f"   -> Encontrado: {os.path.basename(archivo_migracion)}")
    
    with open(archivo_migracion, "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazar el error del número 1 por valores válidos
    # Buscamos "default=1" en campos de fecha y hora y los cambiamos
    
    # Corrección para DateField (Fecha)
    new_content = content.replace("models.DateField(default=1)", "models.DateField(default='2024-01-01')")
    
    # Corrección para TimeField (Hora)
    new_content = new_content.replace("models.TimeField(default=1)", "models.TimeField(default='00:00')")
    
    # Corrección para CharField (Texto - Nombre/Apellido) - El 1 se convierte en texto "1", eso no da error técnico pero se ve feo.
    # Mejor lo cambiamos a "Desconocido"
    new_content = new_content.replace("models.CharField(default=1,", "models.CharField(default='Desconocido',")
    
    # Corrección para ForeignKey (Usuario/Cliente) - Aquí el 1 sí sirve (es el ID del admin), así que lo dejamos quieto si es un número.

    if new_content != content:
        with open(archivo_migracion, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ ¡Valores corregidos! Se cambiaron los '1' por fechas reales.")
    else:
        print("ℹ️ No se encontraron valores '1' problemáticos en este archivo.")

if __name__ == "__main__":
    arreglar_migracion_0003()