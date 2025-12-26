import re
from pathlib import Path

# Ruta al archivo views.py
path = Path("apps/businesses/views.py")

def reparar_final():
    print(f"🚑 Reparando views.py en: {path}")
    
    if not path.exists():
        print("❌ No encontré el archivo.")
        return

    content = path.read_text(encoding="utf-8")

    # CÓDIGO NUEVO (Sintaxis simplificada a prueba de errores)
    # Usamos concatenación (+=) en lugar de f-strings multilínea para evitar problemas de formato
    nuevo_codigo = '''@csrf_exempt
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
                
                # 5. ENVIAR TELEGRAM (Construcción segura del mensaje)
                msg = "💰 *PAGO BOLD CONFIRMADO*\\n"
                msg += f"👤 Cliente: {cliente}\\n"
                msg += f"🆔 Orden: #{order_id}\\n"
                msg += "-----------------------------\\n"
                msg += f"💵 Total: ${total:,.0f}\\n"
                msg += f"✅ Abono: ${abono:,.0f}\\n"
                msg += f"👉 *PENDIENTE: ${pendiente:,.0f}*\\n"
                msg += "-----------------------------\\n"
                msg += "📅 Cita Agendada."

                send_telegram_notification(salon, msg)
                
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return HttpResponse(status=405)'''

    # Regex para encontrar el bloque roto (desde el decorador hasta el return final)
    pattern = r'@csrf_exempt\s+def bold_webhook.*?return HttpResponse\(status=405\)'

    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, nuevo_codigo, content, flags=re.DOTALL)
        path.write_text(new_content, encoding="utf-8")
        print("✅ ¡REPARADO! Se reemplazó el webhook roto por uno con sintaxis segura.")
    else:
        print("⚠️ No encontré el bloque exacto. Es posible que el archivo esté muy dañado.")
        print("   Intenta restaurar el archivo manualmente o usar git checkout si esto falla.")

if __name__ == "__main__":
    reparar_final()