import os
from pathlib import Path

# Ruta al archivo views.py
path = Path("apps/businesses/views.py")

def reiniciar_views():
    print(f"🔄 Reiniciando views.py en: {path}")
    
    if not path.exists():
        print("❌ Error: No encuentro el archivo.")
        return

    # Leemos el archivo actual
    content = path.read_text(encoding="utf-8")

    # Definimos el Webhook Perfecto (Versión Blindada)
    webhook_perfecto = """
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
                
                # 5. ENVIAR TELEGRAM (Construcción segura)
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
                send_telegram_notification(salon, "\\n".join(msgs))
                
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return HttpResponse(status=405)
"""

    # Borramos cualquier rastro del webhook viejo o roto
    import re
    clean_content = re.sub(r'@csrf_exempt\s+def bold_webhook.*?return HttpResponse\(status=405\)', '', content, flags=re.DOTALL)
    
    # Agregamos la versión perfecta al final
    new_content = clean_content.strip() + "\n\n" + webhook_perfecto
    
    path.write_text(new_content, encoding="utf-8")
    print("✅ views.py restaurado con código limpio y seguro.")

if __name__ == "__main__":
    reiniciar_views()