import os

content = """#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
"""

# Escribir el archivo asegurando saltos de línea de Linux (\n)
with open('build.sh', 'w', newline='\n') as f:
    f.write(content)

print("✅ build.sh creado correctamente.")
print("🚀 Ahora sí, vamos a la Fase 2.")