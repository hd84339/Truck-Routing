# Weather-Aware Truck Routing (React + Django)

Enter origin, destination, departure time and load weight → get 3 route options, weather sampled at the
truck's **ETA at each checkpoint** (10/25/50 mi), a risk classification per checkpoint, a recommended route,
and a 0–48 h weather heatmap along the corridor.

## What We Have Built
- **Interactive Map:** Visualizes truck routes with an overlaid weather heatmap powered by `react-leaflet`.
- **Smart Routing & Weather Fusion:** Queries OSRM for routes and Open-Meteo for hourly weather, merging them by calculating the truck's exact ETA at every point along the route.
- **Risk Assessment System:** Evaluates wind, rain, and snow conditions at each checkpoint, overriding risk levels based on truck load weight (e.g. restricting High Profile trucks in high winds).
- **Time-Scrubber:** A slider to scrub through the next 48 hours of weather data across the route to find the safest departure window.

## Run locally (Windows)
```powershell
# 1. Start the Backend (Port 8000)
cd backend
py -m pip install -r requirements.txt
py manage.py runserver

# 2. Start the Frontend (Port 5173) - Run in a separate terminal
cd frontend
npm install
npm run dev
```

No API keys needed. Hosted: `docker build -t trucks . && docker run -p 8000:8000 trucks` (Render/Fly/Railway all work).

## Architecture
| Piece | Choice | Why |
|---|---|---|
| Routing | OSRM public API (`alternatives=true`) | Free, no key. If <3 distinct routes come back, left/right via-point detours are added, de-duplicated by geometric overlap, and detours >1.5× fastest are dropped. |
| Geocoding | Nominatim (also accepts `lat,lng`) | Free, no key |
| Weather | Open-Meteo hourly (wind mph, rain+showers mm→in/hr, snowfall cm→in/hr) | Free, batch endpoint (50 points/call, parallel, cached 15 min) |
| Backend | Django, single `POST /api/plan`, no DB | Stateless; `risk.py` is pure Python and unit-tested |
| Frontend | React + Vite, react-leaflet, `leaflet.heat` | Heatmap updates via `setLatLngs` — no re-render of the map on slider drag |

### Logic (`backend/routing/risk.py`)
- **ETA** at checkpoint = departure + route duration × (mile / total); duration is OSRM time × `TRUCK_TIME_FACTOR` (1.1).
- Weather is read from the forecast hour nearest the ETA. Checkpoint risk = worst of wind/rain/snow, then load overrides
  (≥55 mph NT; 45–54 mph & >30k lb NT; 35–44 mph & >40k lb Severe).
- **Miles per level**: each checkpoint owns half the gap to each neighbour (mile-weighted, not count-weighted).
- **Ranking** (lexicographic): no No-Travel miles → fewest Severe(+NT) miles → fewest High miles → lowest mile-weighted
  average risk → shortest time. The response includes a human-readable explanation.
- **Heatmap**: every checkpoint carries 49 risk values (conditions at departure+0…48 h); the slider just picks an index.

## Known limitations / next steps
- OSRM is a car profile: no truck height/weight restrictions (swap `services.get_routes` for ORS/HERE/Mapbox truck profiles).
- ETA is proportional to distance; no hours-of-service breaks or traffic. Forecast limited to 14 days.
- Rain/snow band edges (e.g. exactly 0.25 in/hr) are ambiguous in the spec; upper edge is treated as the lower band.
- Public OSRM/Nominatim are rate-limited — fine for a demo, use a keyed provider in production.
