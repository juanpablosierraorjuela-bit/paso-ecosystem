import os

# Script de emergencia para forzar la actualización de la DB en Render
# Este script crea una nueva migración y la manda a la nube.

def reparar():
    print("🚑 Iniciando reparación de Base de Datos en Render...")
    
    # 1. Crear migraciones localmente para asegurar que existen
    os.system("python manage.py makemigrations businesses")
    print("✅ Migraciones locales generadas.")

    # 2. Instrucciones para el usuario (La parte manual es necesaria por seguridad)
    print("\n⚠️ IMPORTANTE: Sigue estos pasos EXACTOS en tu terminal AHORA:")
    print("---------------------------------------------------------")
    print("1. git add .")
    print("2. git commit -m 'Fix missing address column in Render DB'")
    print("3. git push")
    print("---------------------------------------------------------")
    print("\n👉 Al hacer 'git push', Render detectará el cambio y aplicará")
    print("   la actualización automáticamente. Espera a que diga 'Live'.")

if __name__ == "__main__":
    reparar()