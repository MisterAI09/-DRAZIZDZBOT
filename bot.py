import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- خادم الويب (Koyeb/Render) ---
server = Flask('')
@server.route('/')
def home(): return "Bot ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ is Active!"

def run_server():
    server.run(host='0.0.0.0', port=8080)

# --- محرك التحميل الشامل ---
# ⚠️ استبدل هذا بالتوكن الخاص بك
BOT_TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 أهلاً بك في بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔\n\n"
        "يمكنني التحميل من:\n"
        "• منصة X (تويتر)\n"
        "• يوتيوب (YouTube)\n"
        "• تيك توك (TikTok)\n"
        "• فيسبوك وانستغرام\n\n"
        "فقط أرسل الرابط الآن! 🚀"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري جلب الفيديو من منصة X/Twitter...")

    ydl_opts = {
        # جلب أفضل جودة ممكنة للمنصة
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        # محاكاة متصفح لتجنب حظر تويتر
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'max_filesize': 48 * 1024 * 1024, # 48MB
    }

    try:
        loop = asyncio.get_event_loop()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخراج المعلومات والتحميل
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)
            # التأكد من الامتداد بعد الدمج
            if not os.path.exists(filename):
                filename = filename.rsplit('.', 1)[0] + ".mp4"

        await status_msg.edit_text("🚀 جاري الرفع لتلجرام...")
        
        with open(filename, 'rb') as video:
            await update.message.reply_video(
                video=video, 
                caption=f"✅ تم التحميل من منصة X\nبواسطة: ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔"
            )
        
        if os.path.exists(filename): os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text("❌ عذراً، لم أتمكن من تحميل هذا الفيديو. قد يكون الحساب خاصاً (Private) أو الفيديو كبيراً جداً.")

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ Bot is starting...")
    app.run_polling(drop_pending_updates=True)
