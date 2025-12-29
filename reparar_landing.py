import os

print("🚑 Reparando enlace en la página de inicio...")

file_path = os.path.join('templates', 'home_landing.html')

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Reemplazamos el nombre viejo por el nuevo
    if "url 'registro_owner'" in content:
        new_content = content.replace("url 'registro_owner'", "url 'register_owner'")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ ¡Archivo {file_path} corregido exitosamente!")
    else:
        print(f"ℹ️ El archivo {file_path} ya parece estar correcto o no se encontró el texto antiguo.")

except FileNotFoundError:
    print(f"❌ No se encontró el archivo: {file_path}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")