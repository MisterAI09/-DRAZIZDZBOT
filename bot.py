import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- 1. خادم ويب لإبقاء البوت نشطاً على Koyeb ---
server = Flask('')
@server.route('/')
def home(): return "Bot is Live!"

def run_server():
    server.run(host='0.0.0.0', port=8000) # تم تغيير المنفذ ليتوافق مع سجلاتك

# --- 2. محرك التحميل الشامل لجميع المنصات ---
# ⚠️ ضع التوكن الخاص بك هنا
BOT_TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌟 بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ جاهز!\nأرسل رابط فيديو من يوتيوب، X، تيك توك، أو فيسبوك.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري محاولة كسر حماية يوتيوب وتحميل الفيديو...")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        # إعدادات لكسر حظر يوتيوب للسيرفرات
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'max_filesize': 48 * 1024 * 1024,
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
        await status_msg.edit_text("❌ يوتيوب يرفض طلب السيرفر حالياً.\nجرب رابطاً آخر أو منصة أخرى مثل TikTok.")

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    
    # الطريقة الصحيحة لبناء التطبيق لتجنب خطأ AttributeError
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    # تشغيل البوت بطريقة متوافقة
    application.run_polling(drop_pending_updates=True)
