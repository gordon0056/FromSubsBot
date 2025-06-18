import asyncio
from aiogram import Bot
from config import settings

async def schedule_publish(delay: float, content: dict):
    await asyncio.sleep(delay)
    bot = Bot(token=settings.API_TOKEN)

    text = content.get("text", "")
    photo = content.get("photo")
    video = content.get("video")

    try:
        if photo:
            await bot.send_photo(
                chat_id=settings.CHANNEL_ID,
                photo=photo,
                caption=f"#fromSubs\n\n{text}"
            )
        elif video:
            await bot.send_video(
                chat_id=settings.CHANNEL_ID,
                video=video,
                caption=f"#fromSubs\n\n{text}"
            )
        else:
            await bot.send_message(
                chat_id=settings.CHANNEL_ID,
                text=f"#fromSubs\n\n{text}"
            )
    finally:
        await bot.session.close()