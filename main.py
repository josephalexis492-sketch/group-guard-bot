import os
import asyncio
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ChatMemberHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ===== CONFIG =====
BOT_TOKEN = os.getenv("8237376549:AAFxiKB_6aBuqnPZLBz17HuZYl4-PMTm8WQ")

# ===== LOGGING =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===== VERIFY TIMER =====
VERIFY_TIME = 60  # seconds


# ===== NEW MEMBER DETECT =====
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.chat_member.new_chat_members:
        user_id = member.id
        chat_id = update.effective_chat.id

        # Restrict user
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False)
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Verify", callback_data=f"verify_{user_id}")]
        ])

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"👋 Welcome {member.first_name}!\n\n"
                 f"Click verify within {VERIFY_TIME} seconds or you will be kicked.",
            reply_markup=keyboard
        )

        # Start timer
        asyncio.create_task(kick_if_not_verified(context, chat_id, user_id))


# ===== VERIFY BUTTON =====
async def verify_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = int(data.split("_")[1])

    if query.from_user.id != user_id:
        await query.answer("This is not your button!", show_alert=True)
        return

    chat_id = query.message.chat.id

    # Unrestrict user
    await context.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
    )

    await query.edit_message_text("✅ You are verified! Welcome!")


# ===== KICK FUNCTION =====
async def kick_if_not_verified(context, chat_id, user_id):
    await asyncio.sleep(VERIFY_TIME)

    try:
        member = await context.bot.get_chat_member(chat_id, user_id)

        if member.status == "restricted":
            await context.bot.ban_chat_member(chat_id, user_id)
            await context.bot.unban_chat_member(chat_id, user_id)
    except:
        pass


# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatMemberHandler(new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CallbackQueryHandler(verify_button, pattern="^verify_"))

    print("✅ Verify Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()