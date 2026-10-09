from .segment_miles import get_segment_weights

def summarize(levels, miles_at, duration_h):
    """Mile-weighted stats. Each checkpoint owns half the gap to each neighbour."""
    w = get_segment_weights(miles_at)
    tot = sum(w) or 1
    mi = lambda pred: round(sum(x for x, l in zip(w, levels) if pred(l)), 1)
    return {
        "severe_mi": mi(lambda l: l == 3), 
        "no_travel_mi": mi(lambda l: l == 4),
        "high_mi": mi(lambda l: l == 2), 
        "avg_risk": round(sum(x * l for x, l in zip(w, levels)) / tot, 3),
        "max_level": max(levels) if levels else 0, 
        "duration_h": round(duration_h, 2)
    }
