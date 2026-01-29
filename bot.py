import os, asyncio, logging, yt_dlp
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات (للمراقبة في سجلات Koyeb)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- خادم الويب لإرضاء Koyeb ---
app = Flask(__name__)
@app.route('/')
def health_check(): return "OK", 200

def run_flask():
    app.run(host='0.0.0.0', port=8000)

# --- محرك التحميل ---
BOT_TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك! بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ شغال الآن ويسمعك.\nأرسل أي رابط فيديو!")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status = await update.message.reply_text("⏳ جاري معالجة الرابط...")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'vid_%(id)s.%(ext)s',
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            path = ydl.prepare_filename(info)
        
        await status.edit_text("🚀 جاري رفع الفيديو...")
        with open(path, 'rb') as f:
            await update.message.reply_video(video=f, caption="✅ تم بواسطة ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔")
        os.remove(path)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ فشل: {str(e)[:100]}")

# --- التشغيل الرئيسي ---
async def main():
    # تشغيل Flask في خيط منفصل
    Thread(target=run_flask, daemon=True).start()
    
    # بناء تطبيق التلجرام
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    # تشغيل البوت
    async with application:
        await application.initialize()
        await application.start()
        print("Bot is Polling...")
        await application.updater.start_polling(drop_pending_updates=True)
        # إبقاء البوت حياً
        while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
