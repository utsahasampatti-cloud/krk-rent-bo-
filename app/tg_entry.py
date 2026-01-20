import os
import asyncio
import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)
log = logging.getLogger("tg_entry")


def _env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing {name}")
    return v


@Dispatcher().message(CommandStart())  # placeholder, will be overridden below
async def _noop(_: Message) -> None:
    # This decorator will not be used; we attach handlers to the real dispatcher in main().
    return


async def _setup_handlers(dp: Dispatcher) -> None:
    @dp.message(CommandStart())
    async def on_start(message: Message) -> None:
        await message.answer("v2 alive ✅ (polling ok)")

    @dp.message()
    async def on_any(message: Message) -> None:
        # Minimal echo so you can see bot is alive.
        # Replace later with your real router/handlers.
        await message.answer("Я живий. Напиши /start 🙂")


async def run_polling_forever(token: str) -> None:
    bot = Bot(token=token)
    dp = Dispatcher()
    await _setup_handlers(dp)

    # This call BLOCKS until cancelled or error
    await dp.start_polling(bot)


async def main() -> None:
    token = _env("BOT_TOKEN")

    # Optional but recommended for your flow; keep check to avoid silent misconfig
    api_base_url: Optional[str] = os.getenv("API_BASE_URL") or os.getenv("API_URL")
    if not api_base_url:
        raise RuntimeError("Missing API_BASE_URL (or API_URL)")

    log.info("tg_entry: env ok. starting telegram polling…")

    # Never exit: restart polling after any crash
    while True:
        try:
            await run_polling_forever(token)
            log.warning("tg_entry: polling exited unexpectedly. restarting in 3s…")
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            log.info("tg_entry: cancelled. exiting.")
            raise
        except Exception:
            log.exception("tg_entry: polling crashed. restarting in 3s…")
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
