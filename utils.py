from aiogram.types import CallbackQuery

def format_post(post, hashtag=""):
    text = post["text"] or ""
    if hashtag:
        text += f"\n\n{hashtag}"
    return text

async def reject_submission(callback: CallbackQuery):
    await callback.message.edit_text("❌ Post has been rejected.")
    await callback.answer("Post rejected.")