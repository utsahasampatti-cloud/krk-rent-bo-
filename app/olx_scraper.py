import re
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin

PRICE_RE = re.compile(r"(\d[\d\s]*)")

def _parse_price(text: str) -> Optional[float]:
    if not text:
        return None
    m = PRICE_RE.search(text.replace("\xa0", " "))
    if not m:
        return None
    val = m.group(1).replace(" ", "")
    try:
        return float(val)
    except:
        return None

def _extract_listings(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    items: List[Dict] = []

    # OLX listings URLs usually contain /d/oferta/
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "/d/oferta/" not in href:
            continue

        url = href if href.startswith("http") else urljoin("https://www.olx.pl", href)
        url = url.split("?")[0]

        # Title: use visible text, but avoid empty/very short
        title = a.get_text(" ", strip=True)
        if not title or len(title) < 5:
            continue

        # Try to find price/location in the nearest card container
        card = a
        for _ in range(6):
            if not card:
                break

            price_el = card.find(attrs={"data-testid": "ad-price"})
            loc_el = card.find(attrs={"data-testid": "location-date"})

            price = _parse_price(price_el.get_text(" ", strip=True) if price_el else "")
            location = None
            if loc_el:
                location = loc_el.get_text(" ", strip=True).split("-")[0].strip()

            if price_el or loc_el:
                items.append(
                    {
                        "url": url,
                        "title": title[:300],
                        "price_value": price,
                        "location": location[:200] if location else None,
                    }
                )
                break

            card = card.parent

    # dedup by url
    seen = set()
    out = []
    for it in items:
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        out.append(it)
    return out

def scrape_olx(olx_url: str, max_pages: int = 2) -> List[Dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari",
        "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    }

    results: List[Dict] = []
    with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
        for page in range(1, max_pages + 1):
            url = olx_url
            if page > 1:
                joiner = "&" if "?" in url else "?"
                url = f"{url}{joiner}page={page}"

            r = client.get(url)
            if r.status_code in (403, 429):
                break
            r.raise_for_status()

            results.extend(_extract_listings(r.text))

    final = {}
    for it in results:
        final[it["url"]] = it
    return list(final.values())
