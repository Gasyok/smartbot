import os
import socket
import hashlib
import socket

# токен бота
TOKEN_BOT = os.environ['TOKEN_BOT']

# hostname вашего сервера
WEBHOOK_HOST = os.environ['HOST']
# адрес вебхука
WEBHOOK_PATH = "/testbot/"+hashlib.sha256(TOKEN_BOT.encode('utf-8')).hexdigest()
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# настройки вебсервера для вебхука

# для сервера
# WEBAPP_HOST = socket.gethostname()
# WEBAPP_PORT = 80

# для тестов
WEBAPP_HOST = 'localhost'
WEBAPP_PORT = 8080