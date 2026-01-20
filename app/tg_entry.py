import os
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# ---------- logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [tg_entry] %(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)


# ---------- helpers ----------
def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing {name}")
    return value


# ---------- handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("v2 alive ✅ polling works")


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Я живий 🙂 Напиши /start")


# ---------- main ----------
async def run_polling_forever() -> None:
    token = require_env("BOT_TOKEN")
    require_env("API_BASE_URL")  # фейлимось рано, якщо не задано

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(None, fallback))

    log.info("tg_entry: starting telegram polling")

    # ⚠️ ВАЖЛИВО: run_polling() БЛОКУЄ ПРОЦЕС
    await app.run_polling(close_loop=False)


async def main() -> None:
    log.info("tg_entry: env ok")

    while True:
        try:
            await run_polling_forever()
            log.warning("tg_entry: polling exited unexpectedly, restart in 3s")
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            log.info("tg_entry: cancelled, exiting")
            raise
        except Exception:
            log.exception("tg_entry: polling crashed, restart in 3s")
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
