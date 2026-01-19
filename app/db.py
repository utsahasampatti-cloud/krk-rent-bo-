from typing import List, Dict, Any
from uuid import UUID
import psycopg
from psycopg.rows import dict_row
from app.settings import settings

def get_conn():
    return psycopg.connect(settings.DATABASE_URL, row_factory=dict_row)

def init_db():
    sql = open("app/models.sql", "r", encoding="utf-8").read()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

def upsert_listings(items: List[Dict[str, Any]]) -> int:
    if not items:
        return 0
    q = """
    INSERT INTO listings (source, url, title, price_value, location, scraped_at)
    VALUES ('olx', %(url)s, %(title)s, %(price_value)s, %(location)s, now())
    ON CONFLICT (url) DO UPDATE SET
      title = EXCLUDED.title,
      price_value = EXCLUDED.price_value,
      location = EXCLUDED.location,
      scraped_at = now()
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(q, items)
        conn.commit()
    return len(items)

def mark_state(user_id: int, listing_id: UUID, state: str):
    q = """
    INSERT INTO user_listing_state (user_id, listing_id, state, updated_at)
    VALUES (%s, %s, %s, now())
    ON CONFLICT (user_id, listing_id)
    DO UPDATE SET state = EXCLUDED.state, updated_at = now()
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (user_id, str(listing_id), state))
        conn.commit()

def fetch_feed_and_mark_seen(user_id: int, limit: int = 10):
    q = """
    SELECT l.id, l.title, l.price_value, l.location, l.url
    FROM listings l
    WHERE NOT EXISTS (
      SELECT 1 FROM user_listing_state u
      WHERE u.user_id = %s AND u.listing_id = l.id
    )
    ORDER BY l.scraped_at DESC
    LIMIT %s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (user_id, limit))
            rows = cur.fetchall()

        if rows:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO user_listing_state (user_id, listing_id, state, updated_at)
                    VALUES (%s, %s, 'seen', now())
                    ON CONFLICT (user_id, listing_id) DO NOTHING
                    """,
                    [(user_id, str(r["id"])) for r in rows],
                )
            conn.commit()

    return rows
