import requests
from django.core.cache import cache

UA = {"User-Agent": "weather-truck-routing/1.0 (assessment project)"}

def geocode(q):
    try:
        lat, lng = [float(x) for x in q.split(",")]
        return {"lat": lat, "lng": lng, "name": q}
    except ValueError:
        pass
    key = "geo:" + q.lower()
    if (hit := cache.get(key)): return hit
    r = requests.get("https://nominatim.openstreetmap.org/search", params={"q": q, "format": "json", "limit": 1},
                     headers=UA, timeout=10)
    r.raise_for_status()
    j = r.json()
    if not j: raise ValueError(f"Could not find location '{q}'")
    out = {"lat": float(j[0]["lat"]), "lng": float(j[0]["lon"]), "name": j[0]["display_name"]}
    cache.set(key, out, 86400)
    return out
