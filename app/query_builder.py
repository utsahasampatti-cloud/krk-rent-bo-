from urllib.parse import urlencode, quote_plus

BASE = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/krakow/"

ROOMS_MAP = {1: "one", 2: "two", 3: "three"}

def build_olx_url(filters: dict) -> str:
    url = BASE

    districts = filters.get("districts") or []
    if districts:
        q = districts[0].strip()
        url = f"{url}q-{quote_plus(q.lower())}/"

    params = {}
    price_max = filters.get("price_max")
    if price_max:
        params["search[filter_float_price:to]"] = str(int(price_max))

    rooms = filters.get("rooms")
    if rooms:
        key = ROOMS_MAP.get(int(rooms))
        if key:
            params["search[filter_enum_rooms][0]"] = key

    if params:
        url = url + "?" + urlencode(params)

    return url
