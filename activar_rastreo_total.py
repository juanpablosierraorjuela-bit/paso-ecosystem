import os
import re
from pathlib import Path

# Ruta al archivo views.py
path = Path("apps/businesses/views.py")

def activar_rastreo():
    print(f"🕵️‍♂️ Instalando sistema de rastreo en: {path}")
    
    if not path.exists():
        print("❌ No encontré el archivo apps/businesses/views.py")
        return

    content = path.read_text(encoding="utf-8")

    # Nuevo Webhook con RASTREO (Logs detallados)
    webhook_espia = """
@csrf_exempt
def bold_webhook(request, salon_id):
    if request.method == 'POST':
        print(f"🔵 [WEBHOOK] INICIO - Intento de conexión para Salón ID: {salon_id}")
        try:
            # 1. Ver qué nos mandan exactamente
            body_unicode = request.body.decode('utf-8')
            print(f"📦 [WEBHOOK] Payload Recibido: {body_unicode}")
            
            try:
                payload = json.loads(body_unicode)
            except:
                print("❌ [WEBHOOK] Error: El cuerpo no es JSON válido.")
                return JsonResponse({'status': 'error'}, status=400)

            salon = get_object_or_404(Salon, id=salon_id)
            
            # 2. BUSQUEDA ID
            ref = payload.get('orderId') or payload.get('order_id') or payload.get('payment_reference') or payload.get('reference')
            
            if not ref:
                print("⚠️ [WEBHOOK] Alerta: No viene 'orderId' en el paquete.")
                return JsonResponse({'status': 'error', 'message': 'No reference'}, status=400)
            
            order_id = str(ref).replace('ORD-', '')
            print(f"🔍 [WEBHOOK] Buscando en Base de Datos la Reserva ID: {order_id}")

            # 3. VALIDAR ESTADO
            tx_status = payload.get('transactionStatus')
            print(f"📊 [WEBHOOK] Estado de transacción Bold: {tx_status} (Esperamos 4)")
            
            if tx_status is not None and int(tx_status) != 4:
                print("⛔ [WEBHOOK] Ignorado: El pago no fue aprobado (Estado distinto a 4).")
                return JsonResponse({'status': 'ignored', 'message': 'Not approved'})

            bookings = Booking.objects.filter(payment_id=order_id)
            
            if bookings.exists():
                print(f"✅ [WEBHOOK] ¡Reserva ENCONTRADA! ({bookings.count()} citas)")
                
                total = sum(b.total_price for b in bookings)
                monto = payload.get('paymentAmount')
                if monto:
                    abono = Decimal(str(monto))
                else:
                    abono = total * (salon.deposit_percentage / 100)
                
                pendiente = total - abono
                cliente = bookings.first().customer_name
                
                # Actualizar DB
                bookings.update(status='paid')
                print("💾 [WEBHOOK] Estado actualizado a 'paid' en BD.")
                
                # 5. ENVIAR TELEGRAM
                print("outbox [WEBHOOK] Intentando enviar Telegram...")
                msgs = [
                    "💰 *PAGO BOLD CONFIRMADO (PRODUCCIÓN)*",
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
                    resultado = send_telegram_notification(salon, "\\n".join(msgs))
                    if resultado:
                        print("🚀 [WEBHOOK] Telegram ENVIADO con éxito.")
                    else:
                        print("⚠️ [WEBHOOK] Telegram FALLÓ (Revisar token/chat_id en Dashboard).")
                except Exception as e_tel:
                    print(f"🔥 [WEBHOOK] Excepción al enviar Telegram: {e_tel}")
                
            else:
                print(f"❌ [WEBHOOK] Error: No existe ninguna reserva con payment_id='{order_id}'")
                
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            print(f"🔥 [WEBHOOK] Error Crítico en el código: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    print(f"⛔ [WEBHOOK] Rechazado: Método {request.method} no permitido (Solo POST).")
    return HttpResponse(status=405)
"""

    # Borramos la versión anterior
    patron_borrar = r'@csrf_exempt\s+def bold_webhook.*?return HttpResponse\(status=405\)'
    if re.search(patron_borrar, content, re.DOTALL):
        content = re.sub(patron_borrar, "", content, flags=re.DOTALL)
    
    # Agregamos la versión espía al final
    path.write_text(content.strip() + "\n\n" + webhook_espia, encoding="utf-8")
    print("✅ Webhook actualizado con logs detallados.")

if __name__ == "__main__":
    activar_rastreo()