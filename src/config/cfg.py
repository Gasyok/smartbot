from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN", "NONE")

WEBHOOK_HOST = "https://5521-2-78-169-222.ngrok.io"
WEBHOOK_PATH = "/webhook/" + TOKEN
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH
WEBAPP_HOST = "localhost"
WEBAPP_PORT = 8000
