import os

# Las rutas a los archivos apps.py
rutas = [
    'apps/core/apps.py',
    'apps/businesses/apps.py',
    'apps/marketplace/apps.py',
    'apps/booking/apps.py'
]

for ruta in rutas:
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # El nombre de la app es la carpeta contenedora (ej: core, businesses)
        app_name = ruta.split('/')[1]
        
        # Corrección: Cambiar name = 'algo' por name = 'apps.algo'
        old_config = f"name = '{app_name}'"
        new_config = f"name = 'apps.{app_name}'"
        
        if old_config in content:
            new_content = content.replace(old_config, new_config)
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f" Corregido: {ruta}")
        else:
            print(f"ℹ Ya estaba listo o no se encontró el patrón en: {ruta}")
    else:
        print(f" Archivo no encontrado: {ruta}")
