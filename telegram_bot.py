# telegram_bot.py – bot con botones ✅ / ❌
import os, pathlib, json, time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from instagrapi import Client, exceptions

TOKEN = os.getenv("TG_TOKEN")
CHAT  = int(os.getenv("TG_CHAT"))

CAPTION = pathlib.Path("caption.txt").read_text().strip()

def publish_reel(video_path: pathlib.Path):
    cl = Client()
    cl.load_settings("session.json")
    cl.delay_range = [2, 5]
    try:
        cl.login(os.getenv("IG_USER"), os.getenv("IG_PASS"))
    except exceptions.LoginRequired:
        raise RuntimeError("⚠️  Sesión IG caducada. Vuelve a iniciar login manual.")
    cl.clip_upload(str(video_path), caption=CAPTION)
    print("Publicado:", video_path.name)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_message(chat_id=CHAT,
                               text="Bot operativo. Usa /send para enviar un vídeo del día.")

async def send_candidate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    vids = sorted(pathlib.Path("downloads").glob("*.mp4"),
                  key=lambda p: p.stat().st_mtime, reverse=True)
    if not vids:
        await ctx.bot.send_message(chat_id=CHAT, text="No hay vídeos hoy.")
        return
    vid = vids[0]
    kb = [[
        InlineKeyboardButton("✅ Publicar", callback_data=f"yes|{vid}"),
        InlineKeyboardButton("❌ Descartar", callback_data=f"no|{vid}")
    ]]
    await ctx.bot.send_video(chat_id=CHAT, video=open(vid, "rb"),
                             caption="¿Publicar este Reel?",
                             reply_markup=InlineKeyboardMarkup(kb))

async def decision(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    action, path = update.callback_query.data.split("|")
    if action == "yes":
        publish_reel(pathlib.Path(path))
        await update.callback_query.answer("🎉 Publicado en IG")
    else:
        await update.callback_query.answer("Descartado.")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("send", send_candidate))
app.add_handler(CallbackQueryHandler(decision))

if __name__ == "__main__":
    app.run_polling()
