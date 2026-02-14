import os
import random
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ChatMemberHandler,
    ContextTypes,
    CommandHandler,
)

BOT_TOKEN = os.getenv("8237376549:AAFYQIci8uwwsyXuwnIud1dQ2ca4zg41gcs")

VERIFY_TIMEOUT = 60
MAX_ATTEMPTS = 3
VERIFICATION_ENABLED = True

stats = {
    "joins": 0,
    "verified": 0,
    "kicked": 0
}

verification_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Advanced Verifier Running")


async def toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global VERIFICATION_ENABLED
    VERIFICATION_ENABLED = not VERIFICATION_ENABLED
    await update.message.reply_text(f"Verification Enabled: {VERIFICATION_ENABLED}")


async def set_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global VERIFY_TIMEOUT
    try:
        VERIFY_TIMEOUT = int(context.args[0])
        await update.message.reply_text(f"Timeout set to {VERIFY_TIMEOUT}s")
    except:
        await update.message.reply_text("Usage: /timeout 60")


async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not VERIFICATION_ENABLED:
        return

    for member in update.chat_member.new_chat_members:
        stats["joins"] += 1
        user_id = member.id
        chat_id = update.effective_chat.id

        # Delete join message
        try:
            await context.bot.delete_message(chat_id, update.chat_member.message.message_id)
        except:
            pass

        await context.bot.restrict_chat_member(
            chat_id,
            user_id,
            ChatPermissions(can_send_messages=False),
        )

        a = random.randint(1, 10)
        b = random.randint(1, 10)
        correct = a + b

        keyboard = [[
            InlineKeyboardButton(str(correct), callback_data=f"v_{user_id}_{correct}")
        ]]

        msg = await context.bot.send_message(
            chat_id,
            f"👋 {member.first_name}, solve:\n\n{a} + {b} = ?\n⏳ {VERIFY_TIMEOUT}s",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        verification_data[user_id] = {
            "answer": correct,
            "chat_id": chat_id,
        }

        context.job_queue.run_once(kick_unverified, VERIFY_TIMEOUT, data=user_id)


async def kick_unverified(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data

    if user_id in verification_data:
        data = verification_data[user_id]
        chat_id = data["chat_id"]

        try:
            await context.bot.ban_chat_member(chat_id, user_id)
            await context.bot.unban_chat_member(chat_id, user_id)
            stats["kicked"] += 1
        except:
            pass

        del verification_data[user_id]


async def verify_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in verification_data:
        return

    data = verification_data[user_id]
    chat_id = data["chat_id"]

    await context.bot.restrict_chat_member(
        chat_id,
        user_id,
        ChatPermissions(can_send_messages=True),
    )

    stats["verified"] += 1
    await query.edit_message_text("✅ Verified!")
    del verification_data[user_id]


def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("toggle", toggle))
    app.add_handler(CommandHandler("timeout", set_timeout))
    app.add_handler(ChatMemberHandler(new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CallbackQueryHandler(verify_button))

    app.run_polling()