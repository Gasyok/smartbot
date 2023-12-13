import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import cfg

logging.basicConfig(level=logging.INFO)
bot = Bot(token=cfg.bot_token.get_secret_value())
dp = Dispatcher()


async def main():
    from handlers import dp

    try:
        await dp.start_polling()
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
