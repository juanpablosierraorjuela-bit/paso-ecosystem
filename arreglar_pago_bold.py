import os
from pathlib import Path

# Ruta al archivo de éxito de reserva
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / 'templates' / 'booking_success.html'

def modernizar_pago_bold():
    print(f"💳 Modernizando pasarela de pago en: {TEMPLATE_PATH}")
    
    if not TEMPLATE_PATH.exists():
        print("❌ No encontré el archivo booking_success.html")
        return

    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Identificamos el bloque del formulario viejo que causa el error 405
    form_viejo_inicio = '<form action="https://checkout.bold.co/payment/init" method="POST">'
    
    if form_viejo_inicio not in content:
        print("   ℹ️ No encontré el formulario viejo (¿quizás ya se actualizó?).")
        return

    # Nuevo código: Script JS oficial de Bold + Botón que lo activa
    # Mantenemos las mismas variables de Django ({{ salon.bold... }})
    nuevo_bloque_pago = """
                    <script src="https://checkout.bold.co/library/boldPaymentButton.js"></script>
                    
                    <div id="bold-container">
                        <button type="button" onclick="pagarConBold()" class="btn btn-dark w-100 py-3 rounded-pill shadow-lg fw-bold fs-5 mt-2">
                            <i class="fas fa-lock me-2 text-warning"></i> Pagar Abono Seguro
                        </button>
                    </div>

                    <script>
                        function pagarConBold() {
                            // Configuración oficial de Bold
                            const checkout = new BoldCheckout({
                                orderId: "{{ order_id }}",
                                currency: "COP",
                                amount: "{{ deposit_amount }}",
                                apiKey: "{{ salon.bold_identity_key }}",
                                integritySignature: "{{ bold_signature }}",
                                description: "Reserva en {{ salon.name }}",
                                redirectionUrl: "{{ request.scheme }}://{{ request.get_host }}/mis-citas/"
                            });
                            
                            checkout.open();
                        }
                    </script>
    """

    # Usamos expresiones regulares para reemplazar todo el bloque del formulario <form>...</form>
    import re
    # Patrón: Desde <form... hasta </form>
    patron = r'<form action="https://checkout\.bold\.co/payment/init".*?</form>'
    
    # Realizamos el reemplazo
    if re.search(patron, content, re.DOTALL):
        nuevo_contenido = re.sub(patron, nuevo_bloque_pago, content, flags=re.DOTALL)
        
        with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        print("   ✅ Formulario obsoleto reemplazado por Bold Smart Button (JS).")
    else:
        print("   ⚠️ No pude reemplazar el bloque automáticamente. Revisa el archivo.")

if __name__ == "__main__":
    modernizar_pago_bold()