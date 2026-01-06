import os

def main():
    print("🚑 AGREGANDO DEPENDENCIAS FALTANTES...")
    
    req_path = 'requirements.txt'
    
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            content = f.read()
            
        # Agregamos pytz si no está
        if 'pytz' not in content:
            with open(req_path, 'a') as f:
                f.write('\npytz\n')
            print("✅ Se agregó 'pytz' a requirements.txt")
        else:
            print("ℹ️ 'pytz' ya estaba en la lista.")
            
    else:
        print("❌ No se encontró requirements.txt")
        return

    print("\n👉 EJECUTA ESTOS COMANDOS PARA REPARAR EL DESPLIEGUE:")
    print("   git add requirements.txt")
    print("   git commit -m 'Fix: Add missing pytz library'")
    print("   git push origin main")

if __name__ == "__main__":
    main()