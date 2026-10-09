"""Pure risk logic (no Django/network) so it is trivially unit-testable."""
LEVELS = ["Low", "Moderate", "High", "Severe", "No Travel"]
EDGES = {"wind": (25, 35, 45, 55), "rain": (0.10, 0.25, 0.50, 1.00), "snow": (0.5, 1.0, 2.0, 3.0)}


def level_for(kind: str, v: float) -> int:
    e = EDGES[kind]
    if kind == "wind":                 # lower bounds inclusive: >=55 is No Travel
        return sum(v >= x for x in e)
    if v < e[0]:                       # rain/snow: 'Low' is < first edge, 'No Travel' is > last edge
        return 0
    return 1 + sum(v > x for x in e[1:])


def assess(wind: float, rain: float, snow: float, load_lb: float):
    """Return (level 0-4, reason) for one checkpoint, applying the load rules."""
    parts = {"wind": level_for("wind", wind), "rain": level_for("rain", rain), "snow": level_for("snow", snow)}
    level = max(parts.values())
    driver = max(parts, key=parts.get)
    reason = f"{driver} {LEVELS[level]}"
    if wind >= 55:
        level, reason = 4, "wind >=55 mph: no travel for any load"
    elif 45 <= wind < 55 and load_lb > 30000:
        level, reason = 4, "wind 45-54 mph with load >30,000 lb: no travel"
    elif 35 <= wind < 45 and load_lb > 40000 and level < 3:
        level, reason = 3, "wind 35-44 mph with load >40,000 lb: severe"
    return level, reason


def summarize(levels, miles_at, duration_h):
    """Mile-weighted stats. Each checkpoint owns half the gap to each neighbour."""
    n = len(levels)
    w = []
    for i in range(n):
        lo = miles_at[i - 1] if i else miles_at[i]
        hi = miles_at[i + 1] if i < n - 1 else miles_at[i]
        w.append((hi - lo) / 2)
    tot = sum(w) or 1
    mi = lambda pred: round(sum(x for x, l in zip(w, levels) if pred(l)), 1)
    return {"severe_mi": mi(lambda l: l == 3), "no_travel_mi": mi(lambda l: l == 4),
            "high_mi": mi(lambda l: l == 2), "avg_risk": round(sum(x * l for x, l in zip(w, levels)) / tot, 3),
            "max_level": max(levels), "duration_h": round(duration_h, 2)}


def rank_key(s):
    """Lower is better: feasibility, Severe(+NoTravel) miles, High miles, avg risk, time."""
    return (s["no_travel_mi"] > 0, s["severe_mi"] + s["no_travel_mi"], s["high_mi"], s["avg_risk"], s["duration_h"])
