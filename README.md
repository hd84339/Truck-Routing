# Weather-Aware Truck Routing (React + Django)

Enter origin, destination, departure time and load weight → get 3 route options, weather sampled at the
truck's **ETA at each checkpoint** (10/25/50 mi), a risk classification per checkpoint, a recommended route,
and a 0–48 h weather heatmap along the corridor.

## What We Have Built
- **Interactive Map:** Visualizes truck routes with an overlaid weather heatmap powered by `react-leaflet`.
- **Fleet Dashboard:** Clean, professional dashboard to compare route options and highlight No-Travel zones.
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

## Deployment
This app uses a multi-stage Docker build to serve both the frontend and backend from a single container.
```bash
docker build -t truck-routing .
docker run -p 8000:8000 truck-routing
```
**Environment Variables**:
- `DEBUG=False` (recommended for production)
- `DJANGO_SECRET_KEY` (must be securely set in production)
- `ALLOWED_HOSTS` (comma-separated list of domains)

You can host this Docker image on any container platform like Render, Fly.io, or Railway.

## Architecture
The application follows a clean, modular architecture:
- **`backend/api/`**: HTTP views, validation, and serialization (`POST /api/plan`).
- **`backend/planning/`**: Orchestrates weather, routing, and risk domains.
- **`backend/routing/`**: Providers (OSRM, Nominatim), haversine math, checkpoint sampling, and ETA calculations.
- **`backend/risk/` & `backend/recommendations/`**: Pure, unit-testable Python logic for risk classification and route ranking.
- **`frontend/src/features/`**: Modular React components for the Trip Form, Route Results, and Map UI.

| Piece | Choice | Why |
|---|---|---|
| Routing | OSRM public API (`alternatives=true`) | Free, no key. If <3 distinct routes come back, left/right via-point detours are added. |
| Geocoding | Nominatim (also accepts `lat,lng`) | Free, no key |
| Weather | Open-Meteo hourly | Free, batch endpoint (50 points/call, parallel, cached 15 min) |
| Backend | Django, modular design, no DB | Stateless. |
| Frontend | React + Vite, react-leaflet, `leaflet.heat` | Heatmap updates via `setLatLngs` — no re-render of the map on slider drag. |

## Known limitations / next steps
- **WARNING: OSRM is a car profile. It does NOT guarantee truck-specific restrictions (height, weight, hazmat).** Swap `routing/providers/osrm.py` for ORS/HERE/Mapbox truck profiles in production.
- ETA is proportional to distance; no hours-of-service breaks or traffic. Forecast limited to 14 days.
- Rain/snow band edges (e.g. exactly 0.25 in/hr) are treated as the lower band.
- Public OSRM/Nominatim are rate-limited — fine for a demo, use a keyed provider in production.
