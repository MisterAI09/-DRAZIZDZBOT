import os, asyncio, yt_dlp
from flask import Flask, render_template_string
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from threading import Thread

# --- 1. واجهة الويب (للمتصفح) ---
app = Flask(__name__)
@app.route('/')
def home():
    return render_template_string('<body style="background:#000;color:#00ff7f;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;"><h1>♔𝐃𝐫.𝐀𝐙𝐈𝐙♔ BOT IS LIVE 🚀</h1></body>')

def run_web():
    app.run(host='0.0.0.0', port=8000)

# --- 2. محرك البوت ---
async def start(update, context):
    await update.message.reply_text("✅ شغال يا بطل! أرسل الرابط الآن.")

async def download(update, context):
    url = update.message.text
    msg = await update.message.reply_text("⏳ جاري التحميل...")
    file = f"vid_{update.effective_user.id}.mp4"
    
    try:
        ydl_opts = {'format': 'best', 'outtmpl': file, 'nocheckcertificate': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        await update.message.reply_video(video=open(file, 'rb'), caption="✅ تم بواسطة ♔𝐃𝐫.𝐀𝐙𝐈𝐙♔")
        os.remove(file)
        await msg.delete()
    except Exception as e:
        await msg.edit_text("❌ فشل التحميل. تأكد من الرابط.")

# --- 3. التشغيل ---
if __name__ == '__main__':
    Thread(target=run_web, daemon=True).start()
    
    # التوكن الخاص بك تم وضعه هنا
    TOKEN = "8223953336:AAEJfwX3Izn7uG8jkQf3DYKdWGCRnXSFzPA"
    
    app_tel = Application.builder().token(TOKEN).build()
    app_tel.add_handler(CommandHandler("start", start))
    app_tel.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    
    print("Bot is running...")
    app_tel.run_polling(drop_pending_updates=True, close_loop=False)
