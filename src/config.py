import os

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
PULSE_API_TOKEN = os.environ["PULSE_API_TOKEN"]

PULSE_API_HOST = os.environ["PULSE_API_HOST"].strip().rstrip("/")
if "://" not in PULSE_API_HOST:
    PULSE_API_HOST = f"https://{PULSE_API_HOST}"

ALLOWED_USER_IDS = {
    int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x.strip()
}
