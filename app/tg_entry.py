import time
import traceback

def run_polling_forever():
    # <-- тут ти підставиш реальний запуск TG polling
    # Наприклад:
    # from app.telegram_bot import run_polling
    # run_polling()
    pass

def main():
    print("tg_entry: env ok. starting telegram polling…", flush=True)

    while True:
        try:
            run_polling_forever()
            # якщо polling чомусь повернувся — це підозріло, але ми не падаємо
            print("tg_entry: polling exited, restarting in 3s…", flush=True)
            time.sleep(3)
        except Exception:
            print("tg_entry: polling crashed. restarting in 3s…", flush=True)
            traceback.print_exc()
            time.sleep(3)

if __name__ == "__main__":
    main()
