import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- إعداد خادم ويب بسيط لإبقاء البوت حياً على Render ---
server = Flask('')

@server.route('/')
def home():
    return "البوت يعمل بنجاح! ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔"

def run_http_server():
    server.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_http_server)
    t.daemon = True
    t.start()

# --- إعدادات البوت والتحميل ---

# ⚠️ ضع التوكن الخاص بك بين علامتي التنصيص بالأسفل
BOT_TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA" 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك في بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔\n\n"
        "أرسل لي أي رابط فيديو (TikTok, YouTube, FB) وسأقوم بتحميله لك فوراً! 🚀"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        return

    status_msg = await update.message.reply_text("⏳ جاري التحميل... انتظر ثانية")

    # إعدادات التحميل
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'quiet': True,
        'max_filesize': 48 * 1024 * 1024, # لا يتجاوز 48 ميجا لضمان الإرسال
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        await status_msg.edit_text("✅ تم التحميل! جاري الرفع لتلجرام...")
        
        with open(filename, 'rb') as video:
            await update.message.reply_video(video, caption="تم التحميل بواسطة ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔")
        
        # حذف الملف من السيرفر بعد الإرسال
        if os.path.exists(filename):
            os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ عذراً، حدث خطأ أثناء التحميل.\n\nتأكد أن الفيديو ليس طويلاً جداً.")

# --- تشغيل البوت ---
if __name__ == '__main__':
    keep_alive() # تشغيل السيرفر الوهمي لإبقاء البوت حياً
    
    # بناء البوت
    print("البوت قيد التشغيل...")
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    application.run_polling()
