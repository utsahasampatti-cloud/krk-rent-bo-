import os
import time

def main():
    # must-have env
    if not os.getenv("BOT_TOKEN"):
        raise RuntimeError("Missing BOT_TOKEN")
    if not (os.getenv("API_BASE_URL") or os.getenv("API_URL")):
        raise RuntimeError("Missing API_BASE_URL")

    print("tg_entry: env ok. starting telegram polling…")

    # TODO: тут має бути реальний запуск TG polling з твого v1
    # Приклади можливих імпортів:
    # from app.telegram_bot import run_polling
    # from app.tg_bot import run_polling
    # from app.bot import run_polling
    # run_polling()

    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
