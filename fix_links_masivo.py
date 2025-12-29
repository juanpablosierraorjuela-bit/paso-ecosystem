import os

print("🕵️‍♂️ Iniciando escaneo y reparación masiva de enlaces...")

# Ruta a la carpeta de templates
templates_dir = 'templates'
count = 0

# Recorremos todos los archivos en la carpeta templates y sus subcarpetas
for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificamos si tiene el nombre viejo (con comilla simple o doble)
                has_error = "url 'registro_owner'" in content or 'url "registro_owner"' in content
                
                if has_error:
                    print(f"🔧 Reparando archivo: {file}")
                    
                    # Reemplazo 1: Comillas simples
                    new_content = content.replace("url 'registro_owner'", "url 'register_owner'")
                    # Reemplazo 2: Comillas dobles (por si acaso)
                    new_content = new_content.replace('url "registro_owner"', "url 'register_owner'")
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    count += 1
            except Exception as e:
                print(f"❌ Error leyendo {file}: {e}")

if count == 0:
    print("✅ No se encontraron archivos con errores. ¡Todo parece estar bien!")
else:
    print(f"✨ ¡Listo! Se repararon {count} archivos.")