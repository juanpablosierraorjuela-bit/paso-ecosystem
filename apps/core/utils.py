import requests
from .models import PlatformSettings

def send_telegram_message(message):
    try:
        config = PlatformSettings.objects.first()
        if not config or not config.telegram_bot_token or not config.telegram_chat_id:
            print("⚠️ Telegram no configurado en el Admin.")
            return False

        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
        data = {
            "chat_id": config.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, data=data, timeout=5)
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error enviando Telegram: {e}")
        return False
