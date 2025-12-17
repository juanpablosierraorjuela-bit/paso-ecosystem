import requests
import logging

logger = logging.getLogger(__name__)

def send_telegram_message(bot_token, chat_id, message):
    """
    Envía mensaje a Telegram. Retorna True si fue exitoso.
    """
    if not bot_token or not chat_id:
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML' # Cambiado a HTML para mejor formato
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if not response.ok:
            logger.error(f"Telegram Error {response.status_code}: {response.text}")
        return response.ok
    except Exception as e:
        logger.error(f"Telegram Connection Error: {e}")
        return False

def notify_new_booking(booking):
    """
    Notifica al dueño del salón y al empleado (si tienen configurado Telegram)
    """
    # 1. Preparar mensaje
    msg = (
        f"🔔 <b>NUEVA RESERVA CONFIRMADA</b>\n\n"
        f"📅 <b>Fecha:</b> {booking.start_time.strftime('%Y-%m-%d %H:%M')}\n"
        f"💇 <b>Servicio:</b> {booking.service.name}\n"
        f"👤 <b>Cliente:</b> {booking.customer_name}\n"
        f"📞 <b>Tel:</b> {booking.customer_phone}\n"
        f"✂️ <b>Estilista:</b> {booking.employee.name}"
    )

    # 2. Notificar al Dueño del Salón
    salon = booking.salon
    if salon.telegram_bot_token and salon.telegram_chat_id:
        send_telegram_message(salon.telegram_bot_token, salon.telegram_chat_id, msg)

    # 3. Notificar al Empleado (si tiene configuración propia)
    emp = booking.employee
    if emp and emp.telegram_bot_token and emp.telegram_chat_id:
        # Evitar doble mensaje si el empleado es el mismo dueño (casos raros)
        if emp.telegram_chat_id != salon.telegram_chat_id:
            send_telegram_message(emp.telegram_bot_token, emp.telegram_chat_id, msg)