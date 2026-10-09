from datetime import timedelta

def calculate_eta(departure, route_duration_h, checkpoint_mile, total_miles):
    """Estimate arrival timestamp at a checkpoint."""
    if total_miles == 0:
        return departure
    return departure + timedelta(hours=route_duration_h * checkpoint_mile / total_miles)
