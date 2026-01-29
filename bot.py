import os
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from threading import Thread

# --- 1. خادم الويب (Koyeb Health Check) ---
app = Flask(__name__)
@app.route('/')
def home(): return "Image AI Bot is Online!", 200

def run_web():
    app.run(host='0.0.0.0', port=8000)

# --- 2. وظيفة توليد الصور ---
def generate_image(prompt):
    # تنظيف النص وتجهيز الرابط
    formatted_prompt = prompt.replace(" ", "%20")
    # نستخدم نموذج Flux المتطور عبر Pollinations
    image_url = f"https://pollinations.ai/p/{formatted_prompt}?width=1024&height=1024&model=flux"
    return image_url

# --- 3. أوامر التلجرام ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎨 مرحباً بك في مختبر ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ للذكاء الاصطناعي!\n\nأرسل لي وصفاً للصورة التي تريدها (مثلاً: A futuristic city) وسأرسمها لك.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    status_msg = await update.message.reply_text("🎨 جاري رسم لوحتك... انتظر قليلاً")
    
    try:
        image_url = generate_image(user_prompt)
        # إرسال الصورة مباشرة من الرابط دون الحاجة لتحميلها على السيرفر (توفيراً للمساحة)
        await update.message.reply_photo(photo=image_url, caption=f"✅ تم رسم: {user_prompt}\nبواسطة: ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ AI")
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text("❌ حدث خطأ أثناء الرسم. حاول مرة أخرى.")

# --- 4. التشغيل ---
if __name__ == '__main__':
    Thread(target=run_web, daemon=True).start()
    
    TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Image Bot is running...")
    application.run_polling(drop_pending_updates=True, close_loop=False)
