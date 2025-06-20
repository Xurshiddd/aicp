import os
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

# Telegram bot tokeni
BOT_TOKEN = os.getenv("BOT_TOKEN")

# MySQL sozlamalari (foydalanilsa)
DB_CONFIG = {
    'host': os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASSWORD", ""),
    'database': os.getenv("DB_NAME", "telegram_bot"),
    'port': int(os.getenv("DB_PORT", 3306)),
}
