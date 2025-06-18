from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from scheduler import schedule_publish
from utils import reject_submission, format_post
from langutils import translate, set_user_language
from keyboards import moderation_keyboard, rejection_reason_keyboard, scheduling_keyboard
from config import settings
import asyncio
from datetime import datetime, timedelta

def escape_markdown(text: str) -> str:
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in text)

pending_posts = {}

def register_handlers(dp: Dispatcher):
    dp.message.register(on_start, F.text == "/start")
    dp.message.register(on_language, F.text == "/language")
    dp.message.register(handle_user_submission, F.text | F.photo | F.video)
    dp.callback_query.register(handle_language_selection, F.data.startswith("lang:"))
    dp.callback_query.register(handle_moderation, F.data.startswith("approve:") | F.data.startswith("reject:"))
    dp.callback_query.register(handle_rejection_reason, F.data.startswith("reject_reason:"))
    dp.callback_query.register(handle_schedule_publish, F.data.startswith("schedule_post:"))
    dp.callback_query.register(reject_submission, F.data.startswith("reject:"))

async def on_start(message: Message):
    await message.answer(translate(message.from_user.id, "welcome"))

async def on_language(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="English", callback_data="lang:en"),
            InlineKeyboardButton(text="Русский", callback_data="lang:ru")
        ]
    ])
    await message.answer(translate(message.from_user.id, "select_language"), reply_markup=kb)

async def handle_language_selection(callback: CallbackQuery):
    lang = callback.data.split(":")[1]
    set_user_language(callback.from_user.id, lang)
    await callback.message.edit_text(translate(callback.from_user.id, "welcome"))

async def handle_user_submission(message: Message):
    post_id = message.message_id
    username = message.from_user.username or "Unknown"
    user_ref = f"@{username}" if username != "Unknown" else f"user_id: {message.from_user.id}"

    text_content = message.text or message.caption or ""
    if not text_content.strip():
        text_content = f"📸 From {user_ref}"

    content = {
        "user_id": message.from_user.id,
        "username": username,
        "text": text_content,
        "photo": message.photo[-1].file_id if message.photo else None,
        "video": message.video.file_id if message.video else None
    }

    pending_posts[post_id] = content

    await message.answer(translate(message.from_user.id, "await_moderation"))

    caption = f"Запрос от {escape_markdown(user_ref)}:\n\n{escape_markdown(text_content)}"
    media = content["photo"] or content["video"]

    if media:
        if content["photo"]:
            await message.bot.send_photo(settings.MODERATOR_CHAT_ID, media, caption=caption,
                                         reply_markup=moderation_keyboard(post_id), parse_mode="MarkdownV2")
        elif content["video"]:
            await message.bot.send_video(settings.MODERATOR_CHAT_ID, media, caption=caption,
                                         reply_markup=moderation_keyboard(post_id), parse_mode="MarkdownV2")
    else:
        await message.bot.send_message(settings.MODERATOR_CHAT_ID, caption,
                                       reply_markup=moderation_keyboard(post_id), parse_mode="MarkdownV2")

async def handle_moderation(callback: CallbackQuery):
    action, post_id = callback.data.split(":")
    post_id = int(post_id)
    post = pending_posts.get(post_id)

    if not post:
        await callback.answer(translate(callback.from_user.id, "moderation_rejected"), show_alert=True)
        return

    if action == "reject":
        await callback.bot.send_message(callback.message.chat.id,
            translate(callback.from_user.id, "rejection_reason"),
            reply_markup=rejection_reason_keyboard(post_id))
    elif action == "approve":
        if callback.message.text:
            await callback.message.edit_text(translate(callback.from_user.id, "moderation_approved"))
        elif callback.message.caption:
            await callback.message.edit_caption(translate(callback.from_user.id, "moderation_approved"))

        await callback.bot.send_message(callback.message.chat.id,
            escape_markdown(format_post(post, hashtag="#fromSubs")),
            reply_markup=scheduling_keyboard(post_id),
            parse_mode="MarkdownV2"
        )

async def handle_rejection_reason(callback: CallbackQuery):
    await callback.message.edit_text("Post rejected. Thank you.")

async def handle_schedule_publish(callback: CallbackQuery):
    post_id = int(callback.data.split(":")[1])
    key = callback.data.split(":")[2]
    post = pending_posts.get(post_id)

    if not post:
        await callback.answer("Post not found.", show_alert=True)
        return

    schedule_map = {
        "10s": 10,
        "10m": 10 * 60,
        "1h": 60 * 60,
        "1d": 24 * 60 * 60,
        "wednesday": (datetime.now().replace(hour=12, minute=0, second=0, microsecond=0) +
                      timedelta((2 - datetime.now().weekday()) % 7 or 7) - datetime.now()).total_seconds()
    }

    delay = schedule_map.get(key, 10)
    asyncio.create_task(schedule_publish(int(delay), post))

    label = "next Wednesday" if key == "wednesday" else key
    await callback.answer(f"Scheduled for {label} from now!")

    if callback.message.text:
        await callback.message.edit_text(f"✅ Post scheduled for {label}.")
    elif callback.message.caption:
        await callback.message.edit_caption(f"✅ Post scheduled for {label}.")

    # Optional debug log
    print(f"⏱ Scheduled post {post_id} for {datetime.now() + timedelta(seconds=delay)}")