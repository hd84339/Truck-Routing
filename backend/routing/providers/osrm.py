import math
import requests
from django.conf import settings
from routing.geometry import hav_mi

UA = {"User-Agent": "weather-truck-routing/1.0 (assessment project)"}
M_PER_MI = 1609.344

def _osrm(pts, alternatives=False):
    path = ";".join(f"{lng},{lat}" for lat, lng in pts)
    r = requests.get(f"https://router.project-osrm.org/route/v1/driving/{path}", headers=UA, timeout=30,
                     params={"alternatives": str(alternatives).lower(), "overview": "full", "geometries": "geojson"})
    if r.status_code != 200: return []
    f = getattr(settings, 'TRUCK_TIME_FACTOR', 1.1)
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
        if r["duration_h"] > 1.5 * c[0]["duration_h"]: continue
        if not any(_similar(r, k) for k in out): out.append(r)
    return out[:3]
