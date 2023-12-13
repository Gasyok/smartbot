from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config import cfg as cfg
from bot import bot, dp
from contextlib import asynccontextmanager
from aiohttp import web
import logging
import uvicorn
from handlers import commands

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
)


WEBHOOK_PATH = cfg.WEBHOOK_PATH
WEBHOOK_URL = cfg.WEBHOOK_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)

    # Register routes
    # dp.include_router(start_router)
    dp.include_router(commands.router)

    yield
    await bot.session.close()
    logger.info("App stopped")


app = FastAPI(lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)


if __name__ == "__main__":
    # web.run_app(app, host=cfg.WEBAPP_HOST, port=cfg.WEBAPP_PORT)
    uvicorn.run(app)