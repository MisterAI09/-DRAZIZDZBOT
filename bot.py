import os
import asyncio
import yt_dlp
from flask import Flask, render_template_string
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from threading import Thread

# --- 1. واجهة الويب الجذابة (HTML) ---
app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ BOT</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1e1e2f, #2a2a40); color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }
        .card { background: rgba(255, 255, 255, 0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); text-align: center; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { font-size: 3rem; margin-bottom: 10px; color: #00d2ff; }
        p { font-size: 1.2rem; color: #ccc; }
        .status { margin-top: 20px; display: inline-block; padding: 10px 20px; border-radius: 50px; background: #28a745; font-weight: bold; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <div class="card">
        <h1>♔𝐃𝐫.𝐀𝐙𝐈𝐙♔</h1>
        <p>بوت التحميل الشامل يعمل الآن بأقصى سرعة 🚀</p>
        <div class="status">● متصل وحي الآن (Active)</div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

def run_web():
    app.run(host='0.0.0.0', port=8000)

# --- 2. محرك البوت (Telegram) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك في بوت ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ الشامل!\nأرسل لي أي رابط وسأقوم بتحميله فوراً.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status = await update.message.reply_text("⏳ جاري التحميل... انتظر قليلاً")
    
    file_name = f"video_{update.effective_user.id}.mp4"
    ydl_opts = {
        'format': 'best',
        'outtmpl': file_name,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        await update.message.reply_video(video=open(file_name, 'rb'), caption="✅ تم التحميل بواسطة ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔")
        os.remove(file_name)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ خطأ: الرابط غير مدعوم أو الملف كبير جداً.")

# --- 3. التشغيل المزدوج ---
if __name__ == '__main__':
    # تشغيل الموقع في خيط منفصل
    Thread(target=run_web, daemon=True).start()
    
    # بناء البوت (ضع التوكن الخاص بك هنا)
    token = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    
    print("🚀 البوت والواجهة يعملان الآن...")
    application.run_polling(drop_pending_updates=True, close_loop=False)
