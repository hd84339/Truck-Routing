from bisect import bisect_left
from routing.geometry import hav_mi

def sample_checkpoints(geom, total_mi, step):
    cum = [0.0]
    for a, b in zip(geom, geom[1:]): cum.append(cum[-1] + hav_mi(a, b))
    scale = total_mi / cum[-1] if cum[-1] else 1
    miles, m = [], 0.0
    while m < total_mi - 1e-6: miles.append(m); m += step
    miles.append(total_mi)
    pts = []
    for m in miles:
        t = min(m / scale, cum[-1]); i = max(1, min(bisect_left(cum, t), len(cum) - 1))
        seg = cum[i] - cum[i - 1] or 1; f = (t - cum[i - 1]) / seg
        a, b = geom[i - 1], geom[i]
        pts.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    return miles, pts
