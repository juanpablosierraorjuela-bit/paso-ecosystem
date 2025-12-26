import os

# CONFIGURACIÓN CORRECTA SEGÚN LA DOCUMENTACIÓN OFICIAL
# Web Service: 'starter' (Sí existe para web)
# Database: 'basic-256mb' (Nombre técnico correcto para el plan de $7)

NUEVO_YAML = """services:
  - type: web
    name: paso-backend
    runtime: docker
    region: oregon
    plan: starter
    branch: main
    numInstances: 1
    healthCheckPath: /
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: paso-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: WEB_CONCURRENCY
        value: "2"

databases:
  - name: paso-db
    region: oregon
    plan: basic-256mb # <--- ¡ESTA ES LA CLAVE! (basic a secas no sirve)
    databaseName: paso_db
    user: paso_admin
"""

def arreglar_yaml():
    ruta = "render.yaml"
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(NUEVO_YAML)
    print("✅ render.yaml corregido con el nombre de plan EXACTO (basic-256mb).")

if __name__ == "__main__":
    arreglar_yaml()