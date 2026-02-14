import os
import random
import logging
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    ContextTypes
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("8237376549:AAFYQIci8uwwsyXuwnIud1dQ2ca4zg41gcs")
VERIFY_TIMEOUT = 60

verification_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Verifier Bot Running")

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.chat_member.new_chat_members:
        chat_id = update.effective_chat.id
        user_id = member.id

        try:
            await context.bot.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(can_send_messages=False)
            )
        except:
            return

        a = random.randint(1, 10)
        b = random.randint(1, 10)
        correct = a + b

        keyboard = [[
            InlineKeyboardButton(str(correct), callback_data=f"verify_{user_id}")
        ]]

        msg = await context.bot.send_message(
            chat_id,
            f"👋 {member.first_name}, solve:\n\n{a} + {b} = ?\n⏳ 60 seconds",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        verification_data[user_id] = {
            "chat_id": chat_id
        }

        context.job_queue.run_once(kick_unverified, VERIFY_TIMEOUT, data=user_id)

async def verify_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in verification_data:
        return

    chat_id = verification_data[user_id]["chat_id"]

    await context.bot.restrict_chat_member(
        chat_id,
        user_id,
        ChatPermissions(can_send_messages=True)
    )

    await query.edit_message_text("✅ Verified!")

    del verification_data[user_id]

async def kick_unverified(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data

    if user_id in verification_data:
        chat_id = verification_data[user_id]["chat_id"]

        try:
            await context.bot.ban_chat_member(chat_id, user_id)
            await context.bot.unban_chat_member(chat_id, user_id)
        except:
            pass

        del verification_data[user_id]

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CallbackQueryHandler(verify_button))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()