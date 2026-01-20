import os
import time

def main():
    # Мінімальна валідація
    if not os.getenv("BOT_TOKEN"):
        raise RuntimeError("Missing BOT_TOKEN")
    if not (os.getenv("API_BASE_URL") or os.getenv("API_URL")):
        raise RuntimeError("Missing API_BASE_URL (or API_URL)")

    print("worker_entry: env ok, starting…")

    # TODO: заміни на реальний старт polling з твого v1
    # Наприклад:
    # from app.telegram_bot import run
    # run()

    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
