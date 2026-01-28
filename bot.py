import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- خادم ويب للبقاء حياً ---
server = Flask('')
@server.route('/')
def home(): return "♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ Bot is Online!"

def run_server():
    server.run(host='0.0.0.0', port=8080)

# --- محرك التحميل الشامل ---
BOT_TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌟 بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ جاهز للخدمة!\nأرسل رابط فيديو من X، تيك توك، أو يوتيوب.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري محاولة كسر الحماية وتحميل الفيديو...")

    ydl_opts = {
        # محاولة جلب أفضل جودة MP4 مباشرة
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'no_warnings': True,
        'quiet': True,
        # أهم جزء لتجاوز الحظر:
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'addreferers': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
    }

    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخراج المعلومات أولاً للتأكد
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("🚀 تم كسر الحماية! جاري الرفع...")
        
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption=f"✅ تم بواسطة ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔\n🎬: {info.get('title')[:50]}")
        
        if os.path.exists(filename): os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text("❌ المنصة ترفض طلب السيرفر حالياً.\nجرب رابطاً آخر أو من موقع مختلف (مثل TikTok).")

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling(drop_pending_updates=True)
