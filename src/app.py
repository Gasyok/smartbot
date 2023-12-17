import logging
import uvicorn

from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from contextlib import asynccontextmanager

from config import cfg
from config.setup import bot, dp
from handlers import user

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
    dp.include_router(user.router)

    yield
    # await bot(DeleteWebhook(drop_pending_updates=True))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()
    logger.info("App stopped")


app = FastAPI(lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)


if __name__ == "__main__":
    uvicorn.run(app)
