import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import settings
from handlers import register_handlers
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=settings.API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)

dp = Dispatcher()

async def main():
    print("✅ Bot is running and polling...")  # 👈 Add this
    register_handlers(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())