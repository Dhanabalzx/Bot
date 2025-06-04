import os
import time
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN", "7853206716:AAGMWNSMeNyyS6OjZPujo8nMnqDjWCjo1LY")
CHAT_ID = os.getenv("CHAT_ID", "771241303")

def get_banknifty():
    try:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20BANK"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
            "Referer": "https://www.nseindia.com/"
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        time.sleep(1)
        response = session.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            for item in data.get("data", []):
                if item.get("symbol") == "BANKNIFTY":
                    ltp = item.get("lastPrice")
                    change = item.get("pChange")
                    return f"BankNifty: {ltp} ({change}%)"
            return "BankNifty not found"
        else:
            return f"NSE Error: {response.status_code}"
    except Exception as e:
        return f"Error fetching BankNifty: {str(e)}"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send message: {e}")

def format_message():
    banknifty = get_banknifty()
    return f"🔔 Market Update:\n\n{banknifty}"


def main():
    while True:
        message = format_message()
        print(f"Sending: {message}")
        send_telegram_message(message)
        time.sleep(900)  # 15 minutes

if __name__ == "__main__":
    main()
