import logging
import asyncio
import config as cfg

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# инициализация бота

loop = asyncio.get_event_loop()
bot = Bot(token=cfg.TOKEN_BOT, parse_mode="HTML", loop=loop)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# команда /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    return await message.reply("Привет!")

# любое отправленное сообщение боту
@dp.message_handler()
async def rep(message: types.Message):
    return await message.reply(message.text)


async def on_startup(dp):
    # Вариант для сервера
    # certificate – этот сертификат нужен для работы бота с самоподписным сертификатом Яндекса.
    # await bot.set_webhook(cfg.WEBHOOK_URL, certificate=open('/etc/ssl/certs/YandexInternalRootCA.pem', 'rb'))

    # Вариант для тестинга
    await bot.set_webhook(cfg.WEBHOOK_URL)


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    await bot.delete_webhook()
    logging.warning('Bye!')


if __name__ == '__main__':
    app = get_new_configured_app(dispatcher=dp, path=cfg.WEBHOOK_PATH)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host=cfg.WEBAPP_HOST, port=cfg.WEBAPP_PORT)