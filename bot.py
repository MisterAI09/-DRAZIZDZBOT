import os
import yt_dlp
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# تفعيل السجلات لمعرفة الأخطاء فوراً
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 1. خادم ويب صغير لإرضاء السيرفر (Koyeb) ---
server = Flask('')
@server.route('/')
def home(): return "البوت يعمل بنجاح!"

def run_server():
    # المنفذ 8000 كما يظهر في إعداداتك بالصور
    server.run(host='0.0.0.0', port=8000)

# --- 2. إعدادات البوت والتحميل ---
# ⚠️ ضع التوكن الخاص بك هنا
BOT_TOKEN = "ضع_التوكن_هنا"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌟 أهلاً بك! أنا بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔\nأرسل رابط فيديو من (YouTube, TikTok, X, Facebook) وسأقوم بتحميله!")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("🔎 جاري التحميل وتجاوز القيود...")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # محاكاة متصفح حقيقي لعدم الحظر
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'max_filesize': 48 * 1024 * 1024, # حد التلجرام 48 ميجا
    }

    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("🚀 تم التحميل! جاري الرفع لتلجرام...")
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption=f"✅ تم بواسطة ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔\n🎬: {info.get('title')[:50]}")
        
        if os.path.exists(filename): os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text("❌ عذراً، لم أستطع تحميل هذا الفيديو. قد يكون محمياً أو حجمه كبير جداً.")

# --- 3. التشغيل الصحيح (يحل مشكلة عدم الاستجابة) ---
if __name__ == '__main__':
    # تشغيل خادم الويب في الخلفية
    Thread(target=run_server, daemon=True).start()
    
    # بناء التطبيق بطريقة Application (الإصدار الجديد)
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    # هذه الطريقة تضمن أن البوت لا ينهار (Crash)
    application.run_polling(drop_pending_updates=True)
