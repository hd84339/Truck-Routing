from datetime import timedelta
import routing
import weather.services
import risk
import recommendations

HEAT_HOURS = 48

def generate_plan(o, d, dep, load, step):
    routes = routing.get_routes((o["lat"], o["lng"]), (d["lat"], d["lng"]))
    if not routes: raise ValueError("No route found")

    sampled = [routing.sample_checkpoints(r["geometry"], r["distance_mi"], step) for r in routes]
    flat = [p for _, pts in sampled for p in pts]
    try: 
        wx = weather.services.fetch_weather(flat)
    except Exception as e: 
        raise Exception(f"Weather service error: {e}")

    out, k = [], 0
    for idx, (r, (miles, pts)) in enumerate(zip(routes, sampled)):
        cps = []
        for m, p in zip(miles, pts):
            w = wx[k]; k += 1; n = len(w["wind"])
            hr = lambda t: min(max(round((t - w["start"]).total_seconds() / 3600), 0), n - 1)
            at = lambda i: (w["wind"][i], w["rain"][i], w["snow"][i])
            eta = routing.calculate_eta(dep, r["duration_h"], m, r["distance_mi"])
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
    return {
        "origin": o,
        "destination": d,
        "routes": out,
        "recommended": best["id"],
        "explanation": recommendations.get_explanation(best["summary"])
    }
