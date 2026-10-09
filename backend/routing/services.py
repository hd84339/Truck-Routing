import math
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from bisect import bisect_left
from django.conf import settings
from django.core.cache import cache

UA = {"User-Agent": "weather-truck-routing/1.0 (assessment project)"}
M_PER_MI = 1609.344


def hav_mi(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))


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


def _osrm(pts, alternatives=False):
    path = ";".join(f"{lng},{lat}" for lat, lng in pts)
    r = requests.get(f"https://router.project-osrm.org/route/v1/driving/{path}", headers=UA, timeout=30,
                     params={"alternatives": str(alternatives).lower(), "overview": "full", "geometries": "geojson"})
    if r.status_code != 200: return []
    f = settings.TRUCK_TIME_FACTOR
    return [{"distance_mi": x["distance"] / M_PER_MI, "duration_h": x["duration"] / 3600 * f,
             "geometry": [(c[1], c[0]) for c in x["geometry"]["coordinates"]]} for x in r.json().get("routes", [])]


def _similar(a, b):
    pa = a["geometry"][::max(1, len(a["geometry"]) // 25)]
    pb = b["geometry"][::max(1, len(b["geometry"]) // 400)]
    return sum(min(hav_mi(p, q) for q in pb) < 1 for p in pa) / len(pa) > 0.85


def get_routes(o, d):
    """Up to 3 distinct routes: OSRM alternatives, topped up with left/right via-point detours."""
    c = _osrm([o, d], True)
    if len(c) < 3:
        k = math.cos(math.radians(o[0]))
        dx, dy = (d[1] - o[1]) * k, d[0] - o[0]
        mid = ((o[0] + d[0]) / 2, (o[1] + d[1]) / 2)
        for s in (0.12, -0.12):
            c += _osrm([o, (mid[0] + s * dx, mid[1] - s * dy / k), d])
    c.sort(key=lambda r: r["duration_h"])
    out = []
    for r in c:
        if r["duration_h"] > 1.5 * c[0]["duration_h"]: continue   # reject silly detours
        if not any(_similar(r, k) for k in out): out.append(r)
    return out[:3]


def sample_checkpoints(geom, total_mi, step):
    cum = [0.0]
    for a, b in zip(geom, geom[1:]): cum.append(cum[-1] + hav_mi(a, b))
    scale = total_mi / cum[-1] if cum[-1] else 1
    miles, m = [], 0.0
    while m < total_mi - 1e-6: miles.append(m); m += step
    miles.append(total_mi)
    pts = []
    for m in miles:
        t = min(m / scale, cum[-1]); i = max(1, min(bisect_left(cum, t), len(cum) - 1))
        seg = cum[i] - cum[i - 1] or 1; f = (t - cum[i - 1]) / seg
        a, b = geom[i - 1], geom[i]
        pts.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    return miles, pts


