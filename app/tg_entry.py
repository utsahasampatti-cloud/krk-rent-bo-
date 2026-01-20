import os
import asyncio
import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tg_entry")

def env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing {name}")
    return v

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("v2 alive ✅")

async def main():
    token = env("BOT_TOKEN")
    env("API_BASE_URL")

    log.info("tg_entry: starting polling…")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))

    await app.run_polling(close_loop=False)

if __name__ == "__main__":
    asyncio.run(main())
