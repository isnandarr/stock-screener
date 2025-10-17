import os
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_test_alert():
    message = "✅ <b>Test Alert Berhasil!</b>\n\nKoneksi dari GitHub ke bot Telegram Anda sudah berfungsi dengan baik."
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        requests.post(url, json=payload)
        print("Pesan tes berhasil dikirim.")
    except Exception as e:
        print(f"Gagal mengirim pesan tes: {e}")

if __name__ == '__main__':
    send_test_alert()
