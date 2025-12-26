import os
import re
from pathlib import Path

# Ruta al archivo views.py
path = Path("apps/businesses/views.py")

def reparar_blindado():
    print(f"🛡️ Reparando views.py con técnica blindada en: {path}")
    
    if not path.exists():
        print("❌ No encontré el archivo.")
        return

    content = path.read_text(encoding="utf-8")

    # CÓDIGO NUEVO (Construido para ser indestructible)
    # Usamos "\n".join() para evitar problemas con comillas triples o saltos de línea en el archivo
    nuevo_webhook = """
@csrf_exempt
def bold_webhook(request, salon_id):
    if request.method == 'POST':
        try:
            salon = get_object_or_404(Salon, id=salon_id)
            payload = json.loads(request.body)
            
            # 1. BUSQUEDA ID
            ref = payload.get('orderId') or payload.get('order_id') or payload.get('payment_reference') or payload.get('reference')
            if not ref:
                return JsonResponse({'status': 'error', 'message': 'No reference'}, status=400)
            order_id = str(ref).replace('ORD-', '')

            # 2. VALIDAR ESTADO
            tx_status = payload.get('transactionStatus')
            if tx_status is not None and int(tx_status) != 4:
                return JsonResponse({'status': 'ignored', 'message': 'Not approved'})

            bookings = Booking.objects.filter(payment_id=order_id)
            if bookings.exists():
                total = sum(b.total_price for b in bookings)
                monto = payload.get('paymentAmount')
                if monto:
                    abono = Decimal(str(monto))
                else:
                    abono = total * (salon.deposit_percentage / 100)
                
                pendiente = total - abono
                cliente = bookings.first().customer_name
                
                bookings.update(status='paid')
                
                # 5. ENVIAR TELEGRAM (Construcción segura por lista)
                lineas_msg = [
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
                msg = "\\n".join(lineas_msg)

                send_telegram_notification(salon, msg)
                
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return HttpResponse(status=405)
"""

    # 1. Eliminar cualquier versión anterior del webhook (buena o mala)
    # Buscamos desde el decorador hasta el return final
    patron_borrar = r'@csrf_exempt\s+def bold_webhook.*?return HttpResponse\(status=405\)'
    
    if re.search(patron_borrar, content, re.DOTALL):
        content = re.sub(patron_borrar, "", content, flags=re.DOTALL)
        print("   🧹 Versión anterior eliminada.")
    else:
        print("   ℹ️ No encontré versión anterior (o estaba muy rota).")

    # 2. Agregar la versión nueva al final del archivo
    # Aseguramos que haya imports necesarios al principio
    if "from decimal import Decimal" not in content:
        content = "from decimal import Decimal\n" + content
    if "import json" not in content:
        content = "import json\n" + content

    # Escribimos el archivo con la nueva función al final
    path.write_text(content + "\n" + nuevo_webhook, encoding="utf-8")
    print("   ✅ Nueva versión blindada agregada al final del archivo.")

if __name__ == "__main__":
    reparar_blindado()