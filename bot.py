import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- خادم ويب لإبقاء البوت نشطاً ---
server = Flask('')
@server.route('/')
def home(): return "♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ is ready!"

def run_server():
    server.run(host='0.0.0.0', port=8080)

# --- محرك التحميل الشامل لجميع المنصات ---
# ⚠️ تأكد من وضع التوكن الخاص بك هنا
BOT_TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ أهلاً بك في بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ الشامل!\nأرسل رابط فيديو من يوتيوب، تيك توك، X، أو فيسبوك.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري محاولة جلب الفيديو وتجاوز الحماية...")

    ydl_opts = {
        # جلب أفضل جودة MP4 مباشرة لتجنب مشاكل المعالجة
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        # الإعدادات السحرية لتجاوز حظر يوتيوب
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        'max_filesize': 48 * 1024 * 1024, # حد التلجرام 48MB
    }

    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # التحميل الفعلي
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("🚀 نجحت في جلب الفيديو! جاري الرفع...")
        
        with open(filename, 'rb') as video:
            await update.message.reply_video(
                video=video, 
                caption=f"✅ تم التحميل بواسطة ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔\n🎬: {info.get('title', 'فيديو')[:50]}"
            )
        
        if os.path.exists(filename): os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text("❌ يوتيوب/المنصة ترفض الطلب حالياً.\nجرب رابطاً آخر أو جودة أقل.")

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.run_polling(drop_pending_updates=True)
