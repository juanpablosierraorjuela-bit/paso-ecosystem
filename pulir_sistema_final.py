import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def arreglar_https_webhook():
    ruta_views = BASE_DIR / 'apps' / 'businesses' / 'views.py'
    print(f"🔒 Forzando HTTPS en Webhook: {ruta_views}")
    
    with open(ruta_views, 'r', encoding='utf-8') as f:
        content = f.read()

    # Buscamos la línea donde se genera la URL
    old_line = "webhook_url = request.build_absolute_uri(f'/api/webhooks/bold/{salon.id}/')"
    
    # La reemplazamos por una lógica que fuerza el reemplazo de http a https
    new_block = """    # Generar URL y forzar HTTPS para que Bold lo acepte
    webhook_url = request.build_absolute_uri(f'/api/webhooks/bold/{salon.id}/')
    if 'http://' in webhook_url:
        webhook_url = webhook_url.replace('http://', 'https://')"""

    if old_line in content:
        content = content.replace(old_line, new_block)
        with open(ruta_views, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   ✅ Vista actualizada: El Webhook ahora siempre será HTTPS.")
    else:
        print("   ℹ️ La vista ya parece tener la lógica o no encontré la línea exacta.")

def mejorar_instrucciones_dashboard():
    ruta_html = BASE_DIR / 'templates' / 'owner_dashboard.html'
    print(f"📖 Mejorando instructivos en: {ruta_html}")
    
    with open(ruta_html, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- 1. MEJORAR INSTRUCTIVO TELEGRAM ---
    # Reemplazamos el bloque del acordeón de Telegram por uno PRO con enlaces
    
    # Identificador para buscar
    old_tele_start = '<div class="accordion-body bg-white small text-muted pt-0">'
    
    # Si encontramos la sección, buscaremos reemplazar el contenido interno
    # Usaremos una estrategia de reemplazo por bloque para ser precisos
    
    nuevo_tele_html = """<div class="accordion-body bg-white small text-muted pt-0">
                                                    <ol class="ps-3 mb-0 mt-2 list-group list-group-numbered list-group-flush">
                                                        <li class="list-group-item border-0 p-1">Abrir <a href="https://t.me/BotFather" target="_blank" class="fw-bold text-decoration-none">@BotFather</a> en Telegram.</li>
                                                        <li class="list-group-item border-0 p-1">Enviar el mensaje <code>/newbot</code> y seguir los pasos (ponerle nombre).</li>
                                                        <li class="list-group-item border-0 p-1">Copiar el <strong>Token</strong> rojo que te da y pegarlo aquí abajo.</li>
                                                        <li class="list-group-item border-0 p-1 text-danger fw-bold bg-danger bg-opacity-10 rounded">¡IMPORTANTE! Busca tu nuevo bot y dale al botón "INICIAR" (Start).</li>
                                                        <li class="list-group-item border-0 p-1">Para el Chat ID: Abrir <a href="https://t.me/userinfobot" target="_blank" class="fw-bold text-decoration-none">@userinfobot</a> y copiar el número "Id".</li>
                                                    </ol>
                                                </div>"""

    # Buscamos el bloque viejo (asumiendo que empieza igual)
    # Como el contenido viejo tiene saltos de línea, usamos un regex simple o reemplazo de texto conocido
    texto_viejo_tele = """<div class="accordion-body bg-white small text-muted pt-0">
                                                    <ol class="ps-3 mb-0 mt-2">
                                                        <li class="mb-1">Busca a <strong>@BotFather</strong> en Telegram.</li>
                                                        <li class="mb-1">Escribe <code>/newbot</code> y ponle nombre a tu bot.</li>
                                                        <li class="mb-1">Copia el <strong>Token</strong> que te da y pégalo aquí.</li>
                                                        <li class="mb-1 text-danger fw-bold">¡Dale START a tu nuevo bot en Telegram!</li>
                                                        <li>Busca a <strong>@userinfobot</strong> para obtener tu "Chat ID".</li>
                                                    </ol>
                                                </div>"""
    
    # Normalizamos espacios para el reemplazo (por si acaso)
    if texto_viejo_tele in content:
        content = content.replace(texto_viejo_tele, nuevo_tele_html)
        print("   ✅ Instructivo Telegram mejorado con enlaces.")
    else:
        # Fallback: intentamos reemplazar solo la lista si el div es diferente
        print("   ⚠️ No pude reemplazar Telegram automáticamente (quizás espacios).")


    # --- 2. AGREGAR INSTRUCTIVO BOLD ---
    # Buscamos el header de Bold para insertar el acordeón de ayuda justo debajo
    header_bold = '<h6 class="fw-bold text-danger mb-0"><i class="fas fa-credit-card me-2"></i> Pagos con Bold</h6>\n                                </div>\n                                <div class="card-body">'
    
    instrucciones_bold = """
                                    <div class="accordion mb-3 shadow-sm rounded-3" id="boldHelp">
                                        <div class="accordion-item border-0">
                                            <h2 class="accordion-header">
                                                <button class="accordion-button collapsed py-2 small fw-bold bg-white text-danger" type="button" data-bs-toggle="collapse" data-bs-target="#colBold">
                                                    ❓ ¿Dónde consigo estas llaves?
                                                </button>
                                            </h2>
                                            <div id="colBold" class="accordion-collapse collapse" data-bs-parent="#boldHelp">
                                                <div class="accordion-body bg-white small text-muted pt-0">
                                                    <ol class="ps-3 mb-0 mt-2 list-group list-group-numbered list-group-flush">
                                                        <li class="list-group-item border-0 p-1">Ingresa a tu <a href="https://panel.bold.co/" target="_blank" class="fw-bold text-decoration-none text-danger">Panel de Bold</a>.</li>
                                                        <li class="list-group-item border-0 p-1">Ve al menú <strong>Desarrolladores</strong> &gt; <strong>Integración</strong>.</li>
                                                        <li class="list-group-item border-0 p-1">Copia el "Identity Key" y el "Secret Key" y pégalos aquí.</li>
                                                        <li class="list-group-item border-0 p-1">En la sección <strong>Webhooks</strong> de Bold, pega el enlace que ves abajo (Webhook URL).</li>
                                                        <li class="list-group-item border-0 p-1 fw-bold">Activa el switch de "Habilitar Webhook" en Bold.</li>
                                                    </ol>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    """

    if header_bold in content and "boldHelp" not in content:
        # Insertamos después de <div class="card-body">
        content = content.replace(header_bold, header_bold + instrucciones_bold)
        print("   ✅ Instructivo Bold agregado con enlaces al panel.")
    else:
        print("   ℹ️ Bold ya tiene instructivo o no encontré el punto de inserción.")

    with open(ruta_html, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    print("=== ✨ PULIENDO EL SISTEMA (UX & HTTPS) ===")
    try:
        arreglar_https_webhook()
        mejorar_instrucciones_dashboard()
        print("\n🚀 LISTO. Ejecuta:")
        print("   git add .")
        print("   git commit -m 'Upgrade UX: HTTPS Webhook and Better Docs'")
        print("   git push")
    except Exception as e:
        print(f"❌ Error: {e}")