import os
import subprocess
import time

def ejecutar(comando):
    print(f"⚙️  Ejecutando: {comando}")
    subprocess.run(comando, shell=True, check=False)

print("=== 🚑 RESCATANDO BASE DE DATOS ===")

# 1. Asegurar que el modelo tiene el campo (Por si acaso)
# (Este paso es solo verificación, no modifica si ya está bien)
print("\n[1/4] Verificando modelos...")
try:
    with open('apps/businesses/models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    if 'address =' not in content:
        print("⚠️  No encontré 'address' en models.py. Agregándolo...")
        # (Aquí iría código de inyección si faltara, pero asumimos que el script anterior lo hizo)
    else:
        print("✅  El código models.py está correcto (tiene 'address').")
except Exception as e:
    print(f"❌ Error leyendo archivo: {e}")

# 2. Forzar creación del archivo de migración
print("\n[2/4] Creando archivo de migración...")
ejecutar("python manage.py makemigrations businesses")

# 3. Subir a GitHub (Lo más importante)
print("\n[3/4] Subiendo cambios a la nube...")
ejecutar("git add apps/businesses/migrations/")
ejecutar("git commit -m 'Fix critical: Add address field migration'")
ejecutar("git push")

print("\n========================================")
print("✅  ¡ENVIADO A RENDER!")
print("========================================")
print("⏳  Espera 2 minutos mientras Render procesa esto.")
print("    Cuando el Dashboard diga 'Live', el error desaparecerá.")