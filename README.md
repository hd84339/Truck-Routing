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

## Deployment Guide
This project is configured for deployment with **Vercel** (Frontend) and **Render** (Backend).

### 1. Deploy the Backend (Render)
Create a new **Web Service** on Render connected to this repository.
- **Root Directory**: `backend`
- **Environment**: Python
- **Build Command**: `./build.sh` (or `pip install -r requirements.txt && python manage.py check --deploy`)
- **Start Command**: `gunicorn config.wsgi --bind 0.0.0.0:$PORT`
- **Environment Variables**:
  - `DEBUG`: `False`
  - `DJANGO_SECRET_KEY`: A strong, random string
  - `ALLOWED_HOSTS`: `<your-render-url>.onrender.com` (you will add the Vercel URL later if needed)
  - `CORS_ALLOWED_ORIGINS`: `<your-vercel-url>.vercel.app` (set this after deploying Vercel!)

Once deployed, verify that `<your-render-url>/api/plan` exists (it should return 405 Method Not Allowed on GET, but the server is up).

### 2. Deploy the Frontend (Vercel)
Create a new project on Vercel connected to this repository.
- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variables**:
  - `VITE_API_URL`: The URL of your deployed Render backend (e.g., `https://truck-routing-api.onrender.com`). Do not append `/api/plan`.

Deploy the frontend. Vercel will automatically configure the routing (via `vercel.json`).
**Important Note:** Make sure you update the backend's `CORS_ALLOWED_ORIGINS` on Render with your new Vercel URL, otherwise the API requests will be blocked by CORS!

### Common Troubleshooting
- **CORS Errors**: Double-check `CORS_ALLOWED_ORIGINS` on Render exactly matches your Vercel URL (include `https://` but no trailing slash).
- **Backend 500 Errors**: Ensure `ALLOWED_HOSTS` includes your Render URL.

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
