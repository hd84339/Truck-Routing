import json
from datetime import datetime, timedelta, timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from . import services
import weather.services
import risk
import recommendations

HEAT_HOURS = 48


@csrf_exempt
@require_POST
def plan(request):
    try:
        b = json.loads(request.body)
        dep = datetime.fromisoformat(b["departure"].replace("Z", "+00:00"))
        dep = dep if dep.tzinfo else dep.replace(tzinfo=timezone.utc)
        load, step = float(b["load_lb"]), int(b.get("interval_mi", 25))
        if step not in (10, 25, 50): raise ValueError("interval_mi must be 10, 25 or 50")
        if not 0 <= load <= 100000: raise ValueError("load_lb must be 0-100,000")
        if dep < datetime.now(timezone.utc) - timedelta(hours=1): raise ValueError("Departure is in the past")
        if dep > datetime.now(timezone.utc) + timedelta(days=14): raise ValueError("Forecast covers 14 days max")
        o, d = services.geocode(b["origin"]), services.geocode(b["destination"])
        routes = services.get_routes((o["lat"], o["lng"]), (d["lat"], d["lng"]))
        if not routes: raise ValueError("No route found")
    except (KeyError, ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:  # upstream API failure
        return JsonResponse({"error": f"Upstream service error: {e}"}, status=502)

    # one batched weather call for every checkpoint of every route
    sampled = [services.sample_checkpoints(r["geometry"], r["distance_mi"], step) for r in routes]
    flat = [p for _, pts in sampled for p in pts]
    try: wx = weather.services.fetch_weather(flat)
    except Exception as e: return JsonResponse({"error": f"Weather service error: {e}"}, status=502)

    out, k = [], 0
    for idx, (r, (miles, pts)) in enumerate(zip(routes, sampled)):
        cps = []
        for m, p in zip(miles, pts):
            w = wx[k]; k += 1; n = len(w["wind"])
            hr = lambda t: min(max(round((t - w["start"]).total_seconds() / 3600), 0), n - 1)
            at = lambda i: (w["wind"][i], w["rain"][i], w["snow"][i])
            eta = dep + timedelta(hours=r["duration_h"] * m / r["distance_mi"])
            i, base = hr(eta), hr(dep)
            lvl, why = risk.assess(*at(i), load)
            cps.append({"mile": round(m, 1), "lat": round(p[0], 4), "lng": round(p[1], 4), "eta": eta.isoformat(),
                        "level": lvl, "label": risk.LEVELS[lvl], "reason": why,
                        "wind_mph": round(at(i)[0], 1), "rain_in_hr": round(at(i)[1], 3), "snow_in_hr": round(at(i)[2], 3),
                        "heat": [risk.assess(*at(min(base + h, n - 1)), load)[0] for h in range(HEAT_HOURS + 1)]})
        g = r["geometry"][::max(1, len(r["geometry"]) // 1200)] + [r["geometry"][-1]]
        s = risk.summarize([c["level"] for c in cps], [c["mile"] for c in cps], r["duration_h"])
        s.update(distance_mi=round(r["distance_mi"], 1), eta=cps[-1]["eta"])
        out.append({"id": idx, "summary": s, "geometry": g, "checkpoints": cps})

    ranked = sorted(out, key=lambda x: recommendations.rank_key(x["summary"]))
    best = ranked[0]
    for rank, x in enumerate(ranked): x["rank"] = rank + 1
    return JsonResponse({"origin": o, "destination": d, "routes": out, "recommended": best["id"],
                         "explanation": recommendations.get_explanation(best["summary"])})
