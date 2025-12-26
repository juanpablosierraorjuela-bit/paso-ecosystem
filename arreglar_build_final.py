import os

# El truco está en la línea de collectstatic:
# Le pasamos DATABASE_URL="sqlite:///db.sqlite3" antes del comando.
# Esto obliga a Django a usar SQLite local solo para este paso, ignorando la DB real inaccesible.

DOCKERFILE_CORREGIDO = """FROM python:3.12-slim

# Optimización de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \\
    libpq-dev \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Instalar librerías
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar proyecto
COPY . /app/

# --- CORRECCIÓN CLAVE ---
# Forzamos a usar SQLite temporalmente durante el build
# para que no intente conectar a la DB real (que falla en el build).
RUN DATABASE_URL="sqlite:///db.sqlite3" python manage.py collectstatic --noinput

# Comando de inicio (Aquí sí usará la DB real)
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
"""

def aplicar_parche():
    with open("Dockerfile", "w", encoding="utf-8") as f:
        f.write(DOCKERFILE_CORREGIDO)
    print("✅ Dockerfile parcheado: Ahora collectstatic usará modo 'offline' para no fallar.")

if __name__ == "__main__":
    aplicar_parche()