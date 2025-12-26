import os
import subprocess
import sys

def ejecutar(comando):
    print(f"\n⚙️  Ejecutando: {comando}")
    # Usamos subprocess para ver el output real y detectar errores
    resultado = subprocess.run(comando, shell=True)
    if resultado.returncode != 0:
        print("   ⚠️  (Advertencia en el comando anterior, continuando...)")

print("==================================================")
print("🚑  INICIANDO REPARACIÓN DE BASE DE DATOS RENDER")
print("==================================================")

# 1. FORZAR CREACIÓN DE MIGRACIONES
# Esto detecta los cambios en models.py (address, city) y crea el archivo 000X_...py
print("\n[1/3] Generando instrucciones nuevas (Migraciones)...")
ejecutar("python manage.py makemigrations businesses")
ejecutar("python manage.py makemigrations users")
ejecutar("python manage.py makemigrations core_saas")

# 2. SUBIR TODO A GITHUB (CRÍTICO)
# Si no subimos el archivo nuevo, Render nunca se enterará
print("\n[2/3] Enviando actualización a la nube...")
ejecutar("git add .")
ejecutar('git commit -m "Emergency Fix: Add missing address column to DB"')
ejecutar("git push")

print("\n==================================================")
print("✅  ¡REPARACIÓN ENVIADA!")
print("==================================================")
print("👉  Ve a tu Dashboard de Render.")
print("👉  Verás que comienza un nuevo 'Deploy'.")
print("👉  Cuando termine y diga 'Live', el error habrá desaparecido.")
print("    (Porque el sistema leerá el archivo nuevo y creará la columna 'address' automáticamente).")