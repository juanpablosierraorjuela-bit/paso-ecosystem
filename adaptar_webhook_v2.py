import os
import re
from pathlib import Path

# Ruta al archivo views.py
path = Path("apps/businesses/views.py")

def actualizar_webhook_v2():
    print(f"🧬 Evolucionando Webhook a V2 en: {path}")
    
    if not path.exists():
        print("❌ No encontré el archivo apps/businesses/views.py")
        return

    content = path.read_text(encoding="utf-8")

    # Nuevo Webhook INTELIGENTE (Soporta V1 y V2)
    webhook_v2 = """
@csrf_exempt
def bold_webhook(request, salon_id):
    if request.method == 'POST':
        print(f"🔵 [WEBHOOK V2] Recibido para Salón ID: {salon_id}")
        try:
            body_unicode = request.body.decode('utf-8')
            payload = json.loads(body_unicode)
            
            # --- ESTRATEGIA HÍBRIDA DE EXTRACCIÓN ---
            
            # 1. BUSCAR ID DE REFERENCIA
            # Intento A: Formato V1 (Raíz)
            ref = payload.get('orderId') or payload.get('order_id') or payload.get('payment_reference')
            
            # Intento B: Formato V2 (Anidado en data -> metadata)
            if not ref:
                data_obj = payload.get('data', {})
                if isinstance(data_obj, dict):
                    meta = data_obj.get('metadata', {})
                    ref = meta.get('reference')
            
            if not ref:
                print("⚠️ [WEBHOOK] Fallo: No se encontró 'reference' ni en raíz ni en metadata.")
                return JsonResponse({'status': 'error', 'message': 'No reference found'}, status=400)

            order_id = str(ref).replace('ORD-', '')
            print(f"🔍 [WEBHOOK] ID Detectado: {order_id}")

            # 2. VALIDAR APROBACIÓN
            is_approved = False
            
            # Chequeo V1: transactionStatus = 4
            tx_status = payload.get('transactionStatus')
            if tx_status is not None and int(tx_status) == 4:
                is_approved = True
                
            # Chequeo V2: type = 'SALE_APPROVED'
            if payload.get('type') == 'SALE_APPROVED':
                is_approved = True

            if not is_approved:
                print(f"⛔ [WEBHOOK] Ignorado. No es venta aprobada (Type: {payload.get('type')}, Status: {tx_status})")
                return JsonResponse({'status': 'ignored', 'message': 'Not approved'})

            # 3. PROCESAR RESERVA
            bookings = Booking.objects.filter(payment_id=order_id)
            
            if bookings.exists():
                print(f"✅ [WEBHOOK] ¡Reserva {order_id} ENCONTRADA!")
                
                # Calcular montos
                total = sum(b.total_price for b in bookings)
                
                # Extraer monto pagado (V1 o V2)
                monto_pagado = payload.get('paymentAmount')
                if not monto_pagado:
                    # Intento V2: data -> amount -> total
                    monto_pagado = payload.get('data', {}).get('amount', {}).get('total')
                
                if monto_pagado:
                    abono = Decimal(str(monto_pagado))
                else:
                    abono = total  # Asumimos total si falla la lectura
                
                pendiente = total - abono
                cliente = bookings.first().customer_name
                salon = bookings.first().salon 
                
                bookings.update(status='paid')
                print("💾 Estado actualizado a 'paid'.")
                
                # Notificación Telegram
                msgs = [
                    "💰 *PAGO BOLD CONFIRMADO*",
                    f"👤 Cliente: {cliente}",
                    f"🆔 Orden: #{order_id}",
                    "-----------------------------",
                    f"💵 Total: ${total:,.0f}",
                    f"✅ Abono: ${abono:,.0f}",
                    f"👉 *PENDIENTE: ${pendiente:,.0f}*",
                    "-----------------------------",
                    "📅 Cita Agendada."
                ]
                
                try:
                    send_telegram_notification(salon, "\\n".join(msgs))
                    print("🚀 Telegram enviado.")
                except Exception as e:
                    print(f"⚠️ Fallo Telegram: {e}")
                
            else:
                print(f"❌ [WEBHOOK] Error: No existe reserva con ID {order_id}")

            return JsonResponse({'status': 'ok'})
            
        except Exception as e:
            print(f"🔥 [WEBHOOK] Error Crítico: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return HttpResponse(status=405)
"""

    # Limpieza quirúrgica del webhook anterior
    patron_borrar = r'@csrf_exempt\s+def bold_webhook.*?return HttpResponse\(status=405\)'
    if re.search(patron_borrar, content, re.DOTALL):
        content = re.sub(patron_borrar, "", content, flags=re.DOTALL)
    
    # Inyectar el nuevo código
    path.write_text(content.strip() + "\n\n" + webhook_v2, encoding="utf-8")
    print("✅ Webhook actualizado para soportar formato Bold V2.")

if __name__ == "__main__":
    actualizar_webhook_v2()