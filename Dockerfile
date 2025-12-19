# 1. Usar una imagen oficial de Python ligera y segura
FROM python:3.10-slim

# 2. Configuración para evitar archivos basura y ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo
WORKDIR /app

# 4. Instalar dependencias del sistema (PostgreSQL + Imágenes + Utilidades)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Instalar dependencias de Python
COPY ./requirements /app/requirements
RUN pip install --upgrade pip
RUN pip install -r requirements/base.txt

# 6. Copiar todo el código del proyecto
COPY . /app

# 7. Configurar el script de inicio (start.sh)
COPY ./start.sh /usr/local/bin/start.sh
# Dar permisos de ejecución al script (Vital para que no falle)
RUN chmod +x /usr/local/bin/start.sh

# 8. Exponer el puerto
EXPOSE 8000

# 9. COMANDO DE ARRANQUE MAESTRO
CMD ["/usr/local/bin/start.sh"]