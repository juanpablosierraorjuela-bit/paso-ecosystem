import requests
import logging

logger = logging.getLogger(__name__)

def send_telegram_message(message):
    """
    Envía un mensaje a tu Telegram personal usando la configuración de la DB.
    """
    from .models import PlatformSettings
    try:
        config = PlatformSettings.objects.first()
        if not config or not config.telegram_bot_token or not config.telegram_chat_id:
            logger.warning(" Telegram no configurado en el Admin.")
            return False

        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": config.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        logger.error(f" Error enviando Telegram: {e}")
        return False
