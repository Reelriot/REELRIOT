# job_daily.py – scrape + dispara Telegram
import subprocess, pathlib, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TG_TOKEN"); CHAT = int(os.getenv("TG_CHAT"))
APP = Application.builder().token(TOKEN).build()

def get_video() -> pathlib.Path | None:
    subprocess.run(["python", "reddit_scraper.py"], check=True)
    vids = sorted(pathlib.Path("downloads").glob("*.mp4"),
                  key=lambda p: p.stat().st_mtime, reverse=True)
    return vids[0] if vids else None

async def push(ctx: ContextTypes.DEFAULT_TYPE):
    vid = get_video()
    if not vid:
        await ctx.bot.send_message(chat_id=CHAT, text="⚠️  No se encontró vídeo hoy.")
        return
    kb = [[
        InlineKeyboardButton("✅ Publicar", callback_data=f"yes|{vid}"),
        InlineKeyboardButton("❌ Descartar", callback_data=f"no|{vid}")
    ]]
    await ctx.bot.send_video(chat_id=CHAT, video=open(vid, "rb"),
                             caption="¿Publicar este Reel?",
                             reply_markup=InlineKeyboardMarkup(kb))

async def decision(update, ctx):
    from telegram_bot import publish_reel  # evita duplicar código
    action, path = update.callback_query.data.split("|")
    if action == "yes":
        publish_reel(pathlib.Path(path))
        await update.callback_query.answer("🎉 Publicado en IG")
    else:
        await update.callback_query.answer("Descartado.")

APP.add_handler(CallbackQueryHandler(decision))
APP.job_queue.run_once(push, when=1)

if __name__ == "__main__":
    APP.run_polling()
