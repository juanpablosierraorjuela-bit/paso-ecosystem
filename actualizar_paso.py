import os
import subprocess
import sys

# --- CONFIGURACIÓN ---
# Nombre del archivo HTML que vamos a crear/sobrescribir
archivo_html = "index.html" 
# Mensaje del commit para GitHub
mensaje_commit = "Ajustes PASO: Logo corregido, alcance nacional y diseño centrado"

# --- EL CÓDIGO HTML CORREGIDO ---
contenido_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PASO - El Futuro de la Belleza</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    
    <style>
        /* ESTILOS PERSONALIZADOS PASO */
        
        .hero-section {
            min-height: 100vh;
            /* Fondo oscuro con superposición para que el texto resalte */
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1560066984-138dadb4c035?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: white;
            padding-top: 76px; /* Compensa el menú fijo */
        }

        .navbar {
            backdrop-filter: blur(10px);
            background-color: rgba(0, 0, 0, 0.9) !important;
        }

        .navbar-brand {
            font-weight: 800;
            letter-spacing: 1px;
            font-size: 1.5rem;
        }
    </style>
</head>
<body>

    <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="#">PASO</a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    <li class="nav-item"><a class="nav-link active" href="#inicio">Inicio</a></li>
                    <li class="nav-item"><a class="nav-link" href="#marketplace">Marketplace</a></li>
                    <li class="nav-item"><a class="nav-link" href="#negocios">Para Negocios</a></li>
                    <li class="nav-item ms-lg-3">
                        <a class="btn btn-outline-light rounded-pill px-4" href="#">Ingresar</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <header id="inicio" class="hero-section d-flex align-items-center">
        <div class="container text-center">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    
                    <h1 class="display-3 fw-bold mb-4">🚀 El futuro de la belleza</h1>
                    
                    <p class="lead fs-4 mb-4">
                        Tu estilo, tu tiempo, en un solo lugar.<br>
                        Reserva en los mejores salones, barberías y spas de 
                        <span class="text-warning fw-bold">toda Colombia</span> 
                        sin llamadas ni esperas.
                    </p>
                    
                    <p class="mb-5 text-white-50 fs-5">Simple, rápido y exclusivo.</p>
                    
                    <div class="d-flex justify-content-center gap-3">
                        <a href="#" class="btn btn-primary btn-lg px-5 rounded-pill shadow-lg">Reservar Cita</a>
                        <a href="#" class="btn btn-outline-light btn-lg px-5 rounded-pill">Soy un Negocio</a>
                    </div>

                </div>
            </div>
        </div>
    </header>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

def ejecutar_comando(comando):
    try:
        subprocess.run(comando, shell=True, check=True)
        print(f"✅ Ejecutado: {comando}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar: {comando}")
        print(e)

def main():
    print("🚀 Iniciando actualización automática de PASO...")

    # 1. Crear/Sobrescribir el archivo HTML
    try:
        with open(archivo_html, "w", encoding="utf-8") as f:
            f.write(contenido_html)
        print(f"📄 Archivo {archivo_html} actualizado correctamente.")
    except Exception as e:
        print(f"❌ Error escribiendo el archivo: {e}")
        return

    # 2. Comandos de Git
    print("octocat: Subiendo a GitHub...")
    ejecutar_comando("git add .")
    ejecutar_comando(f'git commit -m "{mensaje_commit}"')
    
    # Intentamos push simple, si falla asume upstream setead
    ejecutar_comando("git push")

    print("✨ ¡Actualización completada!")
    
    # 3. Autodestrucción
    print("💥 Autodestruyendo script...")
    try:
        os.remove(sys.argv[0])
        print("Bye bye! 👋")
    except Exception as e:
        print(f"No me pude borrar a mi mismo: {e}")

if __name__ == "__main__":
    main()