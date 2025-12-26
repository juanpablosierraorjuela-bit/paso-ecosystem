import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VIEWS_PATH = BASE_DIR / 'apps' / 'businesses' / 'views.py'

def aplicar_mejora():
    print(f"📡 Mejorando notificaciones en: {VIEWS_PATH}")
    
    with open(VIEWS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Nueva lógica del Webhook: Más robusta y con cálculo de saldo pendiente
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
            print(f"Webhook recibido: {payload}") # Log para depuración en Render

            # 1. Obtener ID de la orden (Soporta múltiples formatos de Bold)
            ref = payload.get('orderId') or payload.get('order_id') or payload.get('payment_reference') or payload.get('reference')
            
            if not ref:
                print("❌ Error: No se encontró referencia de orden en el webhook.")
                return JsonResponse({'status': 'error', 'message': 'No reference found'}, status=400)

            # Limpiar prefijo ORD- si existe
            order_id = str(ref).replace('ORD-', '')
            
            # 2. Verificar Estado (4 = Aprobado en Bold)
            # Si Bold envía el estado, lo validamos. Si no (pruebas), asumimos éxito.
            tx_status = payload.get('transactionStatus')
            if tx_status is not None and int(tx_status) != 4:
                print(f"⚠️ Pago recibido pero NO aprobado. Estado: {tx_status}")
                return JsonResponse({'status': 'ignored', 'message': 'Payment not approved'})

            bookings = Booking.objects.filter(payment_id=order_id)
            
            if bookings.exists():
                # 3. Cálculos Financieros
                total_servicio = sum(b.total_price for b in bookings)
                
                # Intentamos leer el monto pagado desde Bold, si no, lo calculamos
                monto_bold = payload.get('paymentAmount')
                if monto_bold:
                    abono = Decimal(monto_bold)
                else:
                    # Fallback: Recalcular según porcentaje del salón
                    abono = total_servicio * (salon.deposit_percentage / 100)

                pendiente = total_servicio - abono
                cliente = bookings.first().customer_name
                
                # 4. Actualizar Base de Datos
                bookings.update(status='paid') # Marcar como pagado
                
                # 5. Notificación INTELIGENTE a Telegram
                msg = (
                    f"💰 *¡NUEVO ABONO RECIBIDO!*\n"
                    f"👤 Cliente: {cliente}\n"
                    f"🆔 Orden: #{order_id}\n"
                    f"-----------------------------\n"
                    f"💵 Total Servicio: ${total_servicio:,.0f}\n"
                    f"✅ Abono Bold:     ${abono:,.0f}\n"
                    f"👉 *COBRAR EN LOCAL: ${pendiente:,.0f}*\n"
                    f"-----------------------------\n"
                    f"📅 Cita confirmada exitosamente."
                )
                
                enviado = send_telegram_notification(salon, msg)
                if enviado:
                    print("✅ Notificación enviada a Telegram.")
                else:
                    print("❌ Falló el envío a Telegram (Revisar Token/ChatID).")
                
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            print(f"🔥 Error crítico en Webhook: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return HttpResponse(status=405)
"""

    # Buscamos el bloque viejo para reemplazarlo
    # Usamos una parte única del código viejo como ancla
    ancla_vieja = "@csrf_exempt\ndef bold_webhook(request, salon_id):"
    
    if ancla_vieja in content:
        # Usamos Regex para reemplazar toda la función vieja
        import re
        # Patrón: Desde el decorador hasta el final de la función (antes de la sig función o final)
        patron = r'@csrf_exempt\s+def bold_webhook\(request, salon_id\):.*?return HttpResponse\(status=405\)'
        
        # Realizamos el reemplazo (flag DOTALL permite que . coincida con saltos de línea)
        if re.search(patron, content, re.DOTALL):
            content = re.sub(patron, nuevo_webhook.strip(), content, flags=re.DOTALL)
            
            with open(VIEWS_PATH, 'w', encoding='utf-8') as f:
                f.write(content)
            print("   ✅ Lógica de Notificación y Cobro Pendiente actualizada.")
        else:
            print("   ⚠️ No pude reemplazar automáticamente (la estructura era distinta).")
    else:
        print("   ❌ No encontré la función bold_webhook original.")

if __name__ == "__main__":
    aplicar_mejora()