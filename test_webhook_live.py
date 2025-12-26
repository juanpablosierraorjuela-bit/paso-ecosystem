import requests
import json

# ================= CONFIGURACIÓN =================
# 1. Tu dominio REAL en Render
DOMINIO = "https://paso-backend.onrender.com"

# 2. El ID de tu Salón (mira la URL cuando entras a tu dashboard, ej: /dashboard/1/)
SALON_ID = "1" 

# 3. Un ID de reserva PENDIENTE que tengas en tu base de datos.
# (Crea una cita, llega hasta el pago, copia el código de la URL y pégalo aquí)
ORDER_ID = "PON_AQUI_EL_CODIGO_DE_LA_CITA" 
# Ejemplo: "b8a9c1d2" (SIN el 'ORD-' si lo tuviera)
# =================================================

def probar_webhook():
    url = f"{DOMINIO}/api/webhooks/bold/{SALON_ID}/"
    
    # Simulamos lo que envía Bold exactamente
    payload = {
        "orderId": f"ORD-{ORDER_ID}",  # Bold suele ponerle prefijo
        "transactionStatus": 4,        # 4 significa APROBADO
        "paymentAmount": "50000.00",   # Simulamos un pago
        "paymentStatus": "APPROVED"
    }

    print(f"🚀 Disparando Webhook simulado a: {url}")
    print(f"📦 Datos enviados: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        
        print(f"\n📡 Estado HTTP: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ¡ÉXITO! El servidor aceptó el pago.")
            print("👉 REVISA TU TELEGRAM AHORA. ¿Llegó el mensaje?")
        elif response.status_code == 404:
            print("❌ Error 404: No encontró el salón o la URL está mal escrita.")
        elif response.status_code == 500:
            print("🔥 Error 500: El servidor falló por dentro (revisar Logs de Render).")
            print("   Respuesta:", response.text)
        else:
            print(f"⚠️ Respuesta inesperada: {response.text}")

    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    probar_webhook()