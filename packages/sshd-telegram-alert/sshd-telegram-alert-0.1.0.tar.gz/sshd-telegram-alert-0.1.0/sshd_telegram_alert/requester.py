from dotenv import load_dotenv
import requests
from pathlib import Path


def load_env():
    dotenv_path = Path('/tmp/python-telegram-bot/.env')
    load_dotenv(dotenv_path=dotenv_path)
    return os.getenv('TELEGRAM_TOKEN'), os.getenv('CHAT_ID')

def send_message():
    telegram_token, chat_id = load_env()
    base_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {'chat_id': chat_id, 'text': 'hello world'}
    r = requests.post(url=base_url, data=data)
    if r.status_code == 200:
        logging.info("Message sended")
    else:
        logging.error("Error sending message")
