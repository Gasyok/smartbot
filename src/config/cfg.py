from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN", "NONE")

WEBHOOK_HOST = "158.160.38.146"
WEBHOOK_PATH = "/webhook/" + TOKEN
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = 8000
