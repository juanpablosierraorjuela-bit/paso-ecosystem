import os

path = 'config/settings.py'

def arreglar_seguridad():
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscamos la línea que activa la redirección forzosa y la apagamos
        if "SECURE_SSL_REDIRECT = True" in content:
            new_content = content.replace(
                "SECURE_SSL_REDIRECT = True", 
                "SECURE_SSL_REDIRECT = False  # Render ya maneja el HTTPS"
            )
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Seguridad ajustada: Render ya podrá hacer el Health Check.")
        else:
            print("⚠️ No encontré la línea SECURE_SSL_REDIRECT. Verifica manualmente.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    arreglar_seguridad()