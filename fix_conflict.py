import os
import shutil

def main():
    print("🚑 RESOLVIENDO CONFLICTO DE VERSIONES...")

    # 1. Desactivar apps.booking en SETTINGS.PY
    settings_path = 'config/settings.py'
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            for line in lines:
                # Comentamos la línea que carga la app rota
                if "'apps.booking'" in line or '"apps.booking"' in line:
                    f.write(f"# {line}") 
                    print("✅ Desactivado 'apps.booking' en settings.py")
                else:
                    f.write(line)

    # 2. Desactivar apps.booking en URLS.PY
    urls_path = 'config/urls.py'
    if os.path.exists(urls_path):
        with open(urls_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open(urls_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if "apps.booking.urls" in line:
                    f.write(f"# {line}")
                    print("✅ Desactivado rutas de booking en urls.py")
                else:
                    f.write(line)

    # 3. Renombrar la carpeta problemática para que Python no la vea
    if os.path.exists('apps/booking'):
        try:
            if os.path.exists('apps/booking_deprecated'):
                shutil.rmtree('apps/booking_deprecated') # Limpiar si ya existe
            shutil.move('apps/booking', 'apps/booking_deprecated')
            print("✅ Carpeta 'apps/booking' movida a 'apps/booking_deprecated'")
        except Exception as e:
            print(f"⚠️ No se pudo mover la carpeta (quizás ya estaba movida): {e}")

    print("\n✨ ¡Conflicto resuelto! Ahora Django debería leer solo el código restaurado.")
    print("👉 EJECUTA AHORA:")
    print("   1. python manage.py makemigrations businesses")
    print("   2. python manage.py migrate")
    print("   3. git add .")
    print("   4. git commit -m 'Fix: Disable broken booking app and migration'")
    print("   5. git push origin main")

if __name__ == "__main__":
    main()