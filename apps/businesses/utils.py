import requests

def send_telegram_message(bot_token, chat_id, message):
    """
    Envía un mensaje a Telegram usando la API oficial.
    """
    if not bot_token or not chat_id:
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.ok
    except Exception as e:
        print(f"Error enviando Telegram: {e}")
        return False