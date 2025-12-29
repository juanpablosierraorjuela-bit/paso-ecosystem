import os

# Ruta a tu archivo de configuración
settings_path = 'config/settings.py'

def arreglar_settings():
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # 1. Buscamos la línea de ALLOWED_HOSTS
        if "ALLOWED_HOSTS = [" in contenido or "ALLOWED_HOSTS=[" in contenido:
            # Reemplazamos cualquier configuración vieja por la que permite todo en Render
            nuevo_contenido = contenido.replace(
                "ALLOWED_HOSTS = []", 
                "ALLOWED_HOSTS = ['*']"
            ).replace(
                "ALLOWED_HOSTS = ['localhost', '127.0.0.1']", 
                "ALLOWED_HOSTS = ['*']"
            )
            
            # Si no encontró las anteriores, buscamos la línea y la forzamos
            if "ALLOWED_HOSTS = ['*']" not in nuevo_contenido:
                # Esta es una búsqueda más genérica para reemplazar la línea donde empiece
                lines = nuevo_contenido.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('ALLOWED_HOSTS'):
                        lines[i] = "ALLOWED_HOSTS = ['*']  # Permitir Render"
                        break
                nuevo_contenido = '\n'.join(lines)

            # 2. Aseguramos que CSRF confíe en Render también (Importante para formularios)
            if "CSRF_TRUSTED_ORIGINS" not in nuevo_contenido:
                nuevo_contenido += "\n\n# --- CONFIGURACION RENDER ---\nCSRF_TRUSTED_ORIGINS = ['https://paso-backend.onrender.com']\n"

            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(nuevo_contenido)
            
            print("✅ ¡Settings reparado! Ahora Django aceptará a Render.")
        else:
            print("⚠️ No encontré ALLOWED_HOSTS en tu archivo. Revisa manualmente.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    arreglar_settings()