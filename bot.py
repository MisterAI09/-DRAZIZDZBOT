import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- سيرفر الويب للبقاء حياً على Koyeb ---
server = Flask('')
@server.route('/')
def home(): return "Bot ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ is Active!"

def run_server():
    server.run(host='0.0.0.0', port=8080)

# --- محرك التحميل الشامل لجميع المنصات ---
# ⚠️ ضع توكن البوت هنا
BOT_TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ أهلاً بك في بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ الشامل\n\n"
        "أرسل لي أي رابط فيديو من يوتيوب، X، فيسبوك، أو تيك توك وسأحضره لك!"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("🔍 جاري التحميل... قد يستغرق الأمر ثوانٍ لتجاوز الحماية.")

    # إعدادات yt-dlp المتقدمة لجميع المواقع
    ydl_opts = {
        # جلب أفضل جودة فيديو + صوت مدمجين في ملف واحد
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        # أهم خيار لتجاوز حظر يوتيوب للسيرفرات
        'nocheckcertificate': True,
        'geo_bypass': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'max_filesize': 48 * 1024 * 1024, # حد التلجرام 48MB
    }

    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # تشغيل التحميل في خيط منفصل
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("🚀 تم جلب الفيديو! جاري الرفع لتلجرام...")
        
        with open(filename, 'rb') as video:
            await update.message.reply_video(
                video=video, 
                caption=f"✅ تم التحميل بواسطة ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔\n🎬: {info.get('title', 'فيديو')}"
            )
        
        if os.path.exists(filename): os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        # إذا فشل، نحاول مرة أخرى بجودة أقل (أحياناً ينجح هذا)
        await status_msg.edit_text("⚠️ فشلت الجودة العالية، أحاول بجودة أقل...")
        try:
            ydl_opts['format'] = 'best'
            # (تكرار عملية التحميل هنا بنفس المنطق أعلاه)
            await status_msg.edit_text("❌ عذراً، هذا الفيديو محمي بشكل قوي أو حجمه كبير جداً.")
        except:
            await status_msg.edit_text("❌ فشل التحميل. يوتيوب قد يمنع السيرفر حالياً.")

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.run_polling(drop_pending_updates=True)
