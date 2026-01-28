import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- 1. نظام إبقاء البوت مستيقظاً (Flask Server) ---
server = Flask('')

@server.route('/')
def home():
    return "Bot ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ is Running!"

def run_http_server():
    # المنفذ 8080 هو الافتراضي لمعظم المنصات مثل Koyeb و Render
    server.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_http_server)
    t.daemon = True
    t.start()

# --- 2. إعدادات البوت والتحميل ---

# ⚠️ ضع التوكن الخاص بك هنا
BOT_TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك في بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔\n\n"
        "أرسل لي رابط الفيديو وسأقوم بتحميله لك فوراً! 🚀"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        return

    status_msg = await update.message.reply_text("⏳ جاري التحميل... انتظر ثانية")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'quiet': True,
        'max_filesize': 48 * 1024 * 1024, # حد أقصى 48 ميجابايت
    }

    try:
        # استخدام loop لتجنب حظر العمليات المتزامنة
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        
        await status_msg.edit_text("✅ تم التحميل! جاري الرفع لتلجرام...")
        
        with open(filename, 'rb') as video:
            await update.message.reply_video(video, caption="تم التحميل بواسطة ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔")
        
        if os.path.exists(filename):
            os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ خطأ: قد يكون الملف كبيراً جداً أو الرابط غير مدعوم.")

# --- 3. تشغيل البوت النهائي ---
if __name__ == '__main__':
    # تشغيل خادم الويب أولاً
    keep_alive()
    
    # بناء تطبيق التلجرام
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("Bot ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ has started...")
    
    # تشغيل البوت مع إعدادات التوافق لإصدارات Python الحديثة
    application.run_polling(drop_pending_updates=True)
