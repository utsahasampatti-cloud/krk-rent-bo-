import re
import httpx
from selectolax.parser import HTMLParser
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
    tree = HTMLParser(html)
    items = []

    for a in tree.css("a"):
        href = a.attributes.get("href", "")
        if not href:
            continue
        if "/d/oferta/" not in href:
            continue

        url = href if href.startswith("http") else urljoin("https://www.olx.pl", href)
        title = (a.text() or "").strip()
        if not title or len(title) < 5:
            continue

        card = a.parent
        for _ in range(5):
            if card is None:
                break
            price_node = card.css_first("[data-testid='ad-price']")
            loc_node = card.css_first("[data-testid='location-date']")

            price = _parse_price(price_node.text().strip() if price_node else "")
            location = None
            if loc_node:
                location = loc_node.text().split("-")[0].strip()

            if price_node or loc_node:
                items.append(
                    {
                        "url": url.split("?")[0],
                        "title": title[:300],
                        "price_value": price,
                        "location": location[:200] if location else None,
                    }
                )
                break
            card = card.parent

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
