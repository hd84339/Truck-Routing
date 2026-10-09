from .rules import EDGES, LEVELS

def level_for(kind: str, v: float) -> int:
    e = EDGES[kind]
    if kind == "wind":
        return sum(v >= x for x in e)
    if v < e[0]:
        return 0
    return 1 + sum(v > x for x in e[1:])

def assess(wind: float, rain: float, snow: float, load_lb: float):
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
