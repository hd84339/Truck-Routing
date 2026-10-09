def get_explanation(best_summary):
    why = [
        f"{best_summary['severe_mi'] + best_summary['no_travel_mi']} Severe+ mi",
        f"{best_summary['high_mi']} High mi", 
        f"avg risk {best_summary['avg_risk']}",
        f"{best_summary['duration_h']} h"
    ]
    if best_summary["no_travel_mi"]: 
        why.insert(0, "WARNING: every route hits No-Travel conditions")
    return "Fewest Severe -> High -> avg risk -> time: " + ", ".join(why)
