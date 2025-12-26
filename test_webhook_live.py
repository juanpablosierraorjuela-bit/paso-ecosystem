import requests
import json

# ================= CONFIGURACIÓN =================
# 1. Tu dominio REAL en Render
DOMINIO = "https://paso-backend.onrender.com"

# 2. El ID de tu Salón
SALON_ID = "1" 

# 3. TU CÓDIGO DE CITA REAL
ORDER_ID = "8203009135"  # <--- ID corregido
# =================================================

def probar_webhook():
    url = f"{DOMINIO}/api/webhooks/bold/{SALON_ID}/"
    
    # Simulamos lo que envía Bold
    payload = {
        "orderId": f"ORD-{ORDER_ID}",
        "transactionStatus": 4,        # 4 = APROBADO
        "paymentAmount": "50000.00",   # Simulamos pago de 50k
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
            print("❌ Error 404: La URL es incorrecta o el despliegue en Render falló.")
        elif response.status_code == 500:
            print("🔥 Error 500: Fallo interno (Revisa los logs en Render).")
            print("   Respuesta:", response.text)
        else:
            print(f"⚠️ Respuesta inesperada: {response.text}")

    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    probar_webhook()