import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VIEWS_PATH = BASE_DIR / 'apps' / 'businesses' / 'views.py'

def arreglar_views():
    print(f"🔧 Reparando lógica de pagos y notificaciones en: {VIEWS_PATH}")
    
    with open(VIEWS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. ARREGLAR GENERACIÓN DE URL HTTPS (Para que Bold no rechace el link)
    old_url_logic = "webhook_url = request.build_absolute_uri(f'/api/webhooks/bold/{salon.id}/')"
    new_url_logic = """# Generar URL y forzar HTTPS (Bold requiere HTTPS obligatorio)
    webhook_url = request.build_absolute_uri(f'/api/webhooks/bold/{salon.id}/')
    if 'http://' in webhook_url:
        webhook_url = webhook_url.replace('http://', 'https://')"""
    
    if old_url_logic in content:
        content = content.replace(old_url_logic, new_url_logic)
        print("   ✅ HTTPS forzado en el link del Webhook.")

    # 2. ARREGLAR EL WEBHOOK QUE NO NOTIFICA
    # Reemplazamos la función bold_webhook entera por la versión "Inteligente"
    
    nuevo_webhook = """
# ==============================================================================
# WEBHOOK BOLD MEJORADO (Cálculos y Notificaciones Detalladas)
# ==============================================================================
@csrf_exempt
def bold_webhook(request, salon_id):
    if request.method == 'POST':
        try:
            salon = get_object_or_404(Salon, id=salon_id)
            payload = json.loads(request.body)
            print(f"Webhook recibido: {payload}") # Log para depuración

            # 1. BUSQUEDA INTELIGENTE DEL ID (Soporta todos los formatos de Bold)
            ref = payload.get('orderId') or payload.get('order_id') or payload.get('payment_reference') or payload.get('reference')
            
            if not ref:
                print("❌ Error: No se encontró referencia de orden en el webhook.")
                return JsonResponse({'status': 'error', 'message': 'No reference found'}, status=400)

            # Limpiar prefijo ORD- si existe
            order_id = str(ref).replace('ORD-', '')
            
            # 2. VALIDAR ESTADO (4 = Aprobado en Bold)
            tx_status = payload.get('transactionStatus')
            # Si tx_status existe y NO es 4, ignoramos (pago rechazado o pendiente)
            if tx_status is not None and int(tx_status) != 4:
                print(f"⚠️ Pago no aprobado. Estado: {tx_status}")
                return JsonResponse({'status': 'ignored', 'message': 'Payment not approved'})

            bookings = Booking.objects.filter(payment_id=order_id)
            
            if bookings.exists():
                # 3. CÁLCULOS
                total_servicio = sum(b.total_price for b in bookings)
                
                # Intentamos leer monto pagado desde Bold
                monto_bold = payload.get('paymentAmount')
                if monto_bold:
                    abono = Decimal(str(monto_bold))
                else:
                    abono = total_servicio * (salon.deposit_percentage / 100)

                pendiente = total_servicio - abono
                cliente = bookings.first().customer_name
                
                # 4. ACTUALIZAR DB
                bookings.update(status='paid') # Marcar como pagado
                
                # 5. ENVIAR TELEGRAM
                msg = (
                    f"💰 *¡PAGO BOLD CONFIRMADO!*\n"
                    f"👤 Cliente: {cliente}\n"
                    f"🆔 Orden: #{order_id}\n"
                    f"-----------------------------\n"
                    f"💵 Total Servicio: ${total_servicio:,.0f}\n"
                    f"✅ Abono Recibido: ${abono:,.0f}\n"
                    f"👉 *PENDIENTE EN LOCAL: ${pendiente:,.0f}*\n"
                    f"-----------------------------\n"
                    f"📅 Cita agendada exitosamente."
                )
                
                send_telegram_notification(salon, msg)
                print("✅ Notificación enviada a Telegram.")
                
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            print(f"🔥 Error en Webhook: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return HttpResponse(status=405)
"""

    # Usamos un patrón simple para encontrar y reemplazar la función vieja
    import re
    patron_webhook = r'@csrf_exempt\s+def bold_webhook\(request, salon_id\):.*?return HttpResponse\(status=405\)'
    
    if re.search(patron_webhook, content, re.DOTALL):
        content = re.sub(patron_webhook, nuevo_webhook.strip(), content, flags=re.DOTALL)
        print("   ✅ Webhook actualizado: Ahora detecta cualquier formato de ID y calcula saldos.")
        
        with open(VIEWS_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print("   ⚠️ No encontré el webhook viejo para reemplazar. (¿Ya estaba actualizado?)")

if __name__ == "__main__":
    arreglar_views()