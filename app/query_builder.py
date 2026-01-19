from urllib.parse import urlencode, quote

BASE = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/krakow/"

# Rooms enum allowed by OLX per spec
ROOMS_ALLOWED = {"one", "two", "three", "four", "five_more"}

# Parking allowed human values -> encoded values (as per spec)
PARKING_MAP = {
    "w garażu": "w%20gara%C5%BCu",
    "parking strzeżony": "parking%20strze%C5%BCony",
}

def _district_to_q_segment(d: str) -> str:
    """
    District segment must be Polish with diacritics, words separated by hyphen.
    Example: "Bieżanów Prokocim" -> "Bieżanów-Prokocim"
    DO NOT transliterate.
    """
    d = (d or "").strip()
    d = "-".join([p for p in d.split() if p])
    return d

def build_olx_url(filters: dict) -> str:
    url = BASE

    # District in path q-<POLISH_NAME_WITH_DIACRITICS>
    districts = filters.get("districts") or []
    if districts:
        q = _district_to_q_segment(districts[0])
        # keep diacritics but encode safely in path
        url = f"{url}q-{quote(q)}/"

    params = {}

    # Price
    price_min = filters.get("price_min")
    price_max = filters.get("price_max")
    if price_min is not None:
        params["search[filter_float_price:from]"] = str(int(price_min))
    if price_max is not None:
        params["search[filter_float_price:to]"] = str(int(price_max))

    # Rooms multi-enum
    rooms = filters.get("rooms") or []
    rooms_clean = [r for r in rooms if r in ROOMS_ALLOWED]
    for i, r in enumerate(rooms_clean):
        params[f"search[filter_enum_rooms][{i}]"] = r

    # Pets (Tak/Nie)
    pets = filters.get("pets")
    if pets in ("Tak", "Nie"):
        params["search[filter_enum_pets][0]"] = pets

    # Parking (encoded values in query)
    parking = filters.get("parking") or []
    parking_encoded = []
    for p in parking:
        p = (p or "").strip()
        if p in PARKING_MAP:
            parking_encoded.append(PARKING_MAP[p])
        else:
            # allow already-encoded values if caller passed them
            parking_encoded.append(p)

    for i, p in enumerate(parking_encoded):
        params[f"search[filter_enum_parking][{i}]"] = p

    # Elevator
    elevator = filters.get("elevator")
    if elevator is True:
        params["search[filter_enum_elevator][0]"] = "Tak"

    if params:
        url = url + "?" + urlencode(params, doseq=True)

    return url
