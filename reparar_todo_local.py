import os
import time

def arreglar_docker_compose():
    path = 'docker-compose.yml'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        modified = False
        inside_web_env = False
        
        for line in lines:
            new_lines.append(line)
            # Detectamos el bloque de entorno del servicio web
            if 'web:' in line:
                inside_web_service = True
            if inside_web_service and 'environment:' in line:
                inside_web_env = True
            
            # Si estamos dentro de environment y no hemos agregado DEBUG, lo agregamos
            if inside_web_env and '- DB_PASS=' in line and not modified:
                if not any('DEBUG=True' in l for l in lines):
                    new_lines.append('      - DEBUG=True\n')
                    print("✅ DEBUG=True agregado a docker-compose.yml")
                    modified = True
                inside_web_env = False # Ya terminamos
                inside_web_service = False

        if modified:
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        else:
            print("ℹ️ docker-compose.yml ya estaba configurado o no se pudo modificar auto (verificar manual).")

    except Exception as e:
        print(f"⚠️ No pude editar docker-compose automaticamente: {e}")

def limpiar_base_datos():
    db_file = 'db.sqlite3'
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"🗑️ Base de datos antigua ({db_file}) eliminada para evitar conflictos.")
        except Exception as e:
            print(f"❌ No pude borrar {db_file}: {e}")
    else:
        print("✨ No hay base de datos vieja, todo limpio.")

def main():
    print("🪄 INICIANDO PROTOCOLO MÁGICO DE REPARACIÓN...")
    print("-" * 40)
    
    # 1. Bajar contenedores actuales
    print("⬇️ Deteniendo servidores actuales...")
    os.system("docker-compose down")
    
    # 2. Limpiar base de datos corrupta
    limpiar_base_datos()
    
    # 3. Configurar DEBUG para ver errores
    arreglar_docker_compose()
    
    print("-" * 40)
    print("🚀 LEVANTANDO EL SISTEMA NUEVAMENTE")
    print("⏳ Esto puede tardar unos minutos mientras instala todo...")
    print("👉 Cuando termine, entra a: http://localhost:8000")
    print("-" * 40)
    
    # 4. Levantar todo
    os.system("docker-compose up --build")

if __name__ == "__main__":
    main()