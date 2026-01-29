import os, asyncio, yt_dlp
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from threading import Thread

# --- 1. خادم ويب بسيط جداً لإرضاء Koyeb (Health Check) ---
app = Flask(__name__)
@app.route('/')
def health(): return "STATUS: ACTIVE", 200

def run_web():
    # Koyeb يحتاج الاستجابة على المنفذ 8000
    app.run(host='0.0.0.0', port=8000)

# --- 2. محرك البوت الذكي ---
TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أهلاً بك! بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ يعمل الآن.\nأرسل أي رابط فيديو للتحميل.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return
    
    msg = await update.message.reply_text("⏳ جاري التحميل... قد يستغرق ذلك دقيقة.")
    file_name = f"vid_{update.effective_user.id}.mp4"
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': file_name,
        'nocheckcertificate': True,
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    try:
        # تشغيل التحميل بطريقة لا تعطل البوت
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        await update.message.reply_video(video=open(file_name, 'rb'), caption="✅ تم التحميل بنجاح!")
        os.remove(file_name)
        await msg.delete()
    except Exception as e:
        await msg.edit_text("❌ حدث خطأ. تأكد أن الرابط صحيح أو أن حجم الفيديو ليس ضخماً.")

# --- 3. التشغيل الرئيسي المتزامن ---
if __name__ == '__main__':
    # البدء بتشغيل الويب فوراً ليتجاوز Health Check
    Thread(target=run_web, daemon=True).start()
    
    # بناء البوت وتشغيله
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    
    print("Bot is starting...")
    # استخدام close_loop=False ضروري جداً لتفادي خطأ Python 3.13
    bot_app.run_polling(drop_pending_updates=True, close_loop=False)
