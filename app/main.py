import json
import redis
from fastapi import FastAPI
from app.settings import settings
from app.schemas import SearchRequest, SearchResponse, ListingOut, StateRequest
from app.query_builder import     f = req.filters.model_dump()

    # backward compat: if someone sends rooms as int, map to enum list
    # (safe: your tg-bot can be updated later)
    r = f.get("rooms")
    if isinstance(r, int):
        mapping = {1: "one", 2: "two", 3: "three", 4: "four"}
        f["rooms"] = [mapping.get(r, "five_more")] if r else []

    # backward compat: old field name price_max/price_min could come as price_value
    if "price_max" not in f and "price_max" in req.filters.model_dump():
        f["price_max"] = req.filters.model_dump().get("price_max")

    olx_url = build_olx_url(f)

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
    olx_url = build_olx_url(req.filters.model_dump())
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
