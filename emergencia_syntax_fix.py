import os
import re
from pathlib import Path

# Ruta al archivo dañado
BASE_DIR = Path(__file__).resolve().parent
VIEWS_PATH = BASE_DIR / 'apps' / 'businesses' / 'views.py'

def reparar_sintaxis():
    print(f"🚑 Reparando error de sintaxis en: {VIEWS_PATH}")
    
    if not VIEWS_PATH.exists():
        print("❌ No encontré el archivo views.py")
        return

    with open(VIEWS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- CÓDIGO CORRECTO (Con los saltos de línea protegidos) ---
    webhook_limpio = r"""@csrf_exempt
def bold_webhook(request, salon_id):
    if request.method == 'POST':
        try:
            salon = get_object_or_404(Salon, id=salon_id)
            payload = json.loads(request.body)
            print(f"Webhook recibido: {payload}") 

            # 1. BUSQUEDA INTELIGENTE DEL ID
            ref = payload.get('orderId') or payload.get('order_id') or payload.get('payment_reference') or payload.get('reference')
            
            if not ref:
                print("❌ Error: No se encontró referencia de orden.")
                return JsonResponse({'status': 'error', 'message': 'No reference'}, status=400)

            order_id = str(ref).replace('ORD-', '')
            
            # 2. VALIDAR ESTADO (4 = Aprobado)
            tx_status = payload.get('transactionStatus')
            if tx_status is not None and int(tx_status) != 4:
                return JsonResponse({'status': 'ignored', 'message': 'Not approved'})

            bookings = Booking.objects.filter(payment_id=order_id)
            
            if bookings.exists():
                # 3. CALCULOS
                total_servicio = sum(b.total_price for b in bookings)
                monto_bold = payload.get('paymentAmount')
                
                if monto_bold:
                    abono = Decimal(str(monto_bold))
                else:
                    abono = total_servicio * (salon.deposit_percentage / 100)

                pendiente = total_servicio - abono
                cliente = bookings.first().customer_name
                
                # 4. ACTUALIZAR DB
                bookings.update(status='paid') 
                
                # 5. ENVIAR TELEGRAM (Formato Seguro)
                msg = (
                    f"💰 *¡PAGO BOLD CONFIRMADO!*\n"
                    f"👤 Cliente: {cliente}\n"
                    f"🆔 Orden: #{order_id}\n"
                    f"-----------------------------\n"
                    f"💵 Total: ${total_servicio:,.0f}\n"
                    f"✅ Abono: ${abono:,.0f}\n"
                    f"👉 *PENDIENTE: ${pendiente:,.0f}*\n"
                    f"-----------------------------\n"
                    f"📅 Cita Agendada."
                )
                
                send_telegram_notification(salon, msg)
                print("✅ Telegram enviado.")
                
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            print(f"🔥 Error Webhook: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return HttpResponse(status=405)"""

    # Usamos Regex para encontrar el bloque roto
    # Buscamos desde @csrf_exempt hasta el final de la función (return HttpResponse...)
    # El '.*?' con re.DOTALL atrapará incluso el código roto con saltos de línea malos
    patron_roto = r'@csrf_exempt.*?def bold_webhook.*?return HttpResponse\(status=405\)'
    
    if re.search(patron_roto, content, re.DOTALL):
        # Reemplazamos lo roto por lo limpio
        nuevo_contenido = re.sub(patron_roto, webhook_limpio, content, flags=re.DOTALL)
        
        with open(VIEWS_PATH, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        print("   ✅ Archivo reparado: Se eliminó el error de sintaxis en el f-string.")
    else:
        print("   ⚠️ No pude encontrar el bloque dañado automáticamente. (¿Ya se borró?)")
        # Plan B: Si no lo encuentra por regex, intentamos buscar texto parcial
        if 'f"💰' in content:
            print("   ⚠️ Detecté el f-string roto pero el regex falló. Revisa views.py manualmente.")

if __name__ == "__main__":
    reparar_sintaxis()