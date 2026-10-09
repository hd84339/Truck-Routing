def get_segment_weights(miles_at):
    """Each checkpoint owns half the gap to each neighbour."""
    n = len(miles_at)
    w = []
    for i in range(n):
        lo = miles_at[i - 1] if i else miles_at[i]
        hi = miles_at[i + 1] if i < n - 1 else miles_at[i]
        w.append((hi - lo) / 2)
    return w
