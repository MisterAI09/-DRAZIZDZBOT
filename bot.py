import os
import yt_dlp
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# تفعيل السجلات لمراقبة الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 1. خادم ويب للبقاء حياً على Koyeb (المنفذ 8000 كما في صورك) ---
server = Flask('')
@server.route('/')
def home(): return "♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ Bot is Active!"

def run_server():
    server.run(host='0.0.0.0', port=8000)

# --- 2. محرك التحميل ---
# ⚠️ ضع التوكن الخاص بك هنا
BOT_TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌟 بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ جاهز!\nأرسل رابط فيديو من يوتيوب، X، أو تيك توك.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return
    status_msg = await update.message.reply_text("⏳ جاري محاولة كسر حماية المنصة وتحميل الفيديو...")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
    }

    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("🚀 تم كسر الحماية بنجاح! جاري الرفع...")
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption=f"✅ تم بواسطة ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔\n🎬: {info.get('title')[:50]}")
        
        if os.path.exists(filename): os.remove(filename)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text("❌ المنصة ترفض طلب السيرفر حالياً (خاصة يوتيوب).\nالبوت يعمل، لكن يوتيوب يحظر عناوين IP الخاصة بالسيرفرات.")

# --- 3. تشغيل البوت بطريقة حديثة تمنع الانهيار ---
if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    
    # بناء التطبيق بطريقة Application لضمان التوافق مع Python 3.13
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    # تشغيل البوت (هذا الجزء يحل مشكلة AttributeError في سجلاتك)
    application.run_polling(drop_pending_updates=True)
