import json
import time
import redis
from app.settings import settings
from app.olx_scraper import scrape_olx
from app.db import upsert_listings, init_db

r = redis.from_url(settings.REDIS_URL, decode_responses=True)
QUEUE = "olx_jobs"

def main():
    init_db()
    print("worker: started")

    while True:
        job = r.blpop(QUEUE, timeout=5)
        if not job:
            continue

        _, payload = job
        data = json.loads(payload)

        olx_url = data["olx_url"]
        max_pages = int(data.get("max_pages", settings.OLX_MAX_PAGES))

        time.sleep(settings.OLX_REQUEST_DELAY_SEC)

        try:
            items = scrape_olx(olx_url, max_pages=max_pages)
            upsert_listings(items)
            print(f"worker: scraped {len(items)} from {olx_url}")
        except Exception as e:
            msg = str(e).lower()
            if "403" in msg or "429" in msg:
                time.sleep(10)
            print(f"worker: error {e}")

if __name__ == "__main__":
    main()
