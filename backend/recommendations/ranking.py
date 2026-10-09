def rank_key(s):
    """Lower is better: feasibility, Severe(+NoTravel) miles, High miles, avg risk, time."""
    return (s["no_travel_mi"] > 0, s["severe_mi"] + s["no_travel_mi"], s["high_mi"], s["avg_risk"], s["duration_h"])
