import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ذخیره اطلاعات کاربران
users = {}
chats = {}

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = {
        "step": "name"
    }
    await update.message.reply_text("سلام! لطفاً اسم خودتو وارد کن:")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in users:
        await update.message.reply_text("لطفاً /start رو بزن تا شروع کنیم.")
        return

    step = users[user_id]["step"]

    if step == "name":
        users[user_id]["name"] = text
        users[user_id]["step"] = "gender"
        await update.message.reply_text("جنسیتتو انتخاب کن:", reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("آقا")], [KeyboardButton("خانم")]], resize_keyboard=True
        ))

    elif step == "gender":
        if text not in ["آقا", "خانم"]:
            await update.message.reply_text("لطفاً یکی از گزینه‌های بالا رو انتخاب کن.")
            return
        users[user_id]["gender"] = text
        users[user_id]["step"] = "interest"
        await update.message.reply_text("دنبال چه جنسیتی هستی؟", reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("آقا")], [KeyboardButton("خانم")]], resize_keyboard=True
        ))

    elif step == "interest":
        if text not in ["آقا", "خانم"]:
            await update.message.reply_text("لطفاً یکی از گزینه‌های بالا رو انتخاب کن.")
            return
        users[user_id]["interest"] = text
        users[user_id]["step"] = "city"
        await update.message.reply_text("شهرت رو بنویس:")

    elif step == "city":
        users[user_id]["city"] = text
        users[user_id]["step"] = "photo"
        await update.message.reply_text("یه عکس از خودت بفرست:")

    elif step == "photo":
        await update.message.reply_text("لطفاً یه عکس ارسال کن نه متن.")

    elif user_id in chats:
        partner_id = chats[user_id]
        await context.bot.send_message(partner_id, f"طرف مقابل: {text}")

    else:
        await update.message.reply_text("برای شروع چت /find رو بزن.")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in users and users[user_id]["step"] == "photo":
        photo = update.message.photo[-1].file_id
        users[user_id]["photo"] = photo
        users[user_id]["step"] = "done"
        await update.message.reply_text("پروفایلت ساخته شد! حالا /find رو بزن تا کسی رو پیدا کنیم.")
    else:
        if user_id in chats:
            partner_id = chats[user_id]
            await context.bot.send_photo(partner_id, photo=update.message.photo[-1].file_id)

async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if users[user_id]["step"] != "done":
        await update.message.reply_text("اول پروفایل رو کامل کن بعد /find رو بزن.")
        return

    for other_id, info in users.items():
        if other_id != user_id and info.get("step") == "done" and other_id not in chats:
            if info["gender"] == users[user_id]["interest"] and info["interest"] == users[user_id]["gender"]:
                chats[user_id] = other_id
                chats[other_id] = user_id
                await update.message.reply_text("یه نفر پیدا شد! حالا چت کنید. برای پایان /پایان رو بزن.")
                await context.bot.send_message(other_id, "یه نفر پیدا شد! حالا چت کنید. برای پایان /پایان رو بزن.")
                return

    await update.message.reply_text("فعلاً کسی مطابق با سلیقه‌ت نیست. بعداً دوباره تلاش کن.")

async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in chats:
        partner_id = chats[user_id]
        await context.bot.send_message(partner_id, "چت تموم شد.")
        await update.message.reply_text("چت تموم شد.")
        del chats[partner_id]
        del chats[user_id]
    else:
        await update.message.reply_text("شما در حال چت نیستی.")

def main():
    import os
    TOKEN = os.getenv("TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find))
    app.add_handler(CommandHandler("پایان", end_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    print("ربات روشن شد...")
    app.run_polling()

if __name__ == '__main__':
    main()
