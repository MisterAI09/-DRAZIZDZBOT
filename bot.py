import os
import asyncio
import logging
import yt_dlp
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات لمراقبة Koyeb
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- خادم الويب (Health Check) ---
app = Flask(__name__)
@app.route('/')
def index(): return "البوت شغال 100%", 200

# --- وظائف البوت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ أهلاً! أنا ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔، البوت استيقظ الآن. أرسل رابطاً!")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status = await update.message.reply_text("⏳ جاري التحميل...")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            path = ydl.prepare_filename(info)
        
        await status.edit_text("🚀 جاري الرفع...")
        with open(path, 'rb') as f:
            await update.message.reply_video(video=f, caption="تم بواسطة ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔")
        os.remove(path)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ حدث خطأ: {str(e)[:50]}")

# --- التشغيل المتزامن (الحل السحري) ---
async def main():
    # ⚠️ ضع التوكن هنا
    token = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"
    
    # بناء التطبيق
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    # تشغيل Flask و Telegram معاً
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    
    config = Config()
    config.bind = ["0.0.0.0:8000"]
    
    logger.info("Starting Bot and Web Server...")
    
    # تشغيل البوت والسيرفر في وقت واحد
    await asyncio.gather(
        application.run_polling(drop_pending_updates=True),
        serve(app, config)
    )

if __name__ == '__main__':
    asyncio.run(main())
