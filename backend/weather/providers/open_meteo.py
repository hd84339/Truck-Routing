import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from django.core.cache import cache

def fetch_weather(points):
    """Open-Meteo hourly (16 days, GMT). Returns per point: start, wind mph, rain in/hr, snow in/hr."""
    chunks = [points[i:i + 50] for i in range(0, len(points), 50)]

    def one(ch):
        p = {"latitude": ",".join(f"{a:.3f}" for a, _ in ch), "longitude": ",".join(f"{b:.3f}" for _, b in ch),
             "hourly": "wind_speed_10m,rain,showers,snowfall", "wind_speed_unit": "mph",
             "timezone": "GMT", "forecast_days": 16}
        key = "wx:" + str(sorted(p.items()))
        if (hit := cache.get(key)): return hit
        r = requests.get("https://api.open-meteo.com/v1/forecast", params=p, timeout=30)
        r.raise_for_status()
        j = r.json()
        j = j if isinstance(j, list) else [j]
        cache.set(key, j, 900)
        return j

    with ThreadPoolExecutor(6) as ex: 
        res = [x for part in ex.map(one, chunks) for x in part]
        
    z = lambda v: v or 0
    out = []
    for j in res:
        h = j["hourly"]
        out.append({
            "start": datetime.fromisoformat(h["time"][0]).replace(tzinfo=timezone.utc),
            "wind": [z(v) for v in h["wind_speed_10m"]],
            "rain": [(z(a) + z(b)) / 25.4 for a, b in zip(h["rain"], h["showers"])],
            "snow": [z(v) / 2.54 for v in h["snowfall"]]
        })
    return out
