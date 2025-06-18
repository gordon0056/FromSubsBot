from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def moderation_keyboard(post_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve:{post_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject:{post_id}")
        ]
    ])

def rejection_reason_keyboard(post_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Default reason", callback_data=f"reject_reason:Default reason")],
        [InlineKeyboardButton(text="📉 Does not meet rules", callback_data=f"reject_reason:Does not meet rules")]
    ])

def scheduling_keyboard(post_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏱ 10s", callback_data=f"schedule_post:{post_id}:10s"),
            InlineKeyboardButton(text="🕥 10m", callback_data=f"schedule_post:{post_id}:10m")
        ],
        [
            InlineKeyboardButton(text="🕐 1h", callback_data=f"schedule_post:{post_id}:1h"),
            InlineKeyboardButton(text="📅 1d", callback_data=f"schedule_post:{post_id}:1d")
        ],
        [
            InlineKeyboardButton(text="📆 Next Wed", callback_data=f"schedule_post:{post_id}:wednesday")
        ]
    ])