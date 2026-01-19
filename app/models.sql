CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS listings (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  source text NOT NULL DEFAULT 'olx',
  url text NOT NULL UNIQUE,
  title text NOT NULL,
  price_value numeric NULL,
  location text NULL,
  scraped_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_listing_state (
  user_id bigint NOT NULL,
  listing_id uuid NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
  state text NOT NULL CHECK (state IN ('seen','liked','skipped')),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, listing_id)
);

CREATE INDEX IF NOT EXISTS idx_listings_scraped_at ON listings(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_state_user ON user_listing_state(user_id);
