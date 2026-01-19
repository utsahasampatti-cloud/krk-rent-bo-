import json
import redis
from fastapi import FastAPI

from app.settings import settings
from app.schemas import SearchRequest, SearchResponse, ListingOut, StateRequest
from app.query_builder import build_olx_url
from app.db import init_db, fetch_feed_and_mark_seen, mark_state
from app.utils import new_uuid

app = FastAPI()
r = redis.from_url(settings.REDIS_URL, decode_responses=True)
QUEUE = "olx_jobs"


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    # normalize filters (backward compatible with older tg-bot payloads)
    f = req.filters.model_dump()

    # Backward compat: if someone sends rooms as int (1/2/3/4), map to enum list
    r_in = f.get("rooms")
    if isinstance(r_in, int):
        mapping = {1: "one", 2: "two", 3: "three", 4: "four"}
        f["rooms"] = [mapping.get(r_in, "five_more")] if r_in else []

    # Backward compat: allow old fields if they exist (no-op if already correct)
    # (kept minimal on purpose)
    if "price_max" not in f and hasattr(req.filters, "price_max"):
        f["price_max"] = getattr(req.filters, "price_max")

    if "price_min" not in f and hasattr(req.filters, "price_min"):
        f["price_min"] = getattr(req.filters, "price_min")

    olx_url = build_olx_url(f)
    job_id = new_uuid()

    payload = {
        "job_id": job_id,
        "user_id": req.user_id,
        "olx_url": olx_url,
        "max_pages": 2,
    }
    r.rpush(QUEUE, json.dumps(payload))
    return {"job_id": job_id}


@app.get("/feed", response_model=list[ListingOut])
def feed(user_id: int, limit: int = 10):
    rows = fetch_feed_and_mark_seen(user_id, limit)
    return rows


@app.post("/state")
def state(req: StateRequest):
    mark_state(req.user_id, req.listing_id, req.state)
    return {"ok": True}
