# Loom Walkthrough Outline: Weather-Aware Truck Routing

## 1. Introduction (1 min)
- **Goal:** Introduce the dashboard designed for fleet operators to find the safest route by avoiding severe weather conditions.
- **Context:** Explain that weather conditions (wind, rain, snow) are checked exactly at the truck's ETA for each point along the route, not just at the origin or destination.
- **Visuals:** Briefly show the clean, navy/lime professional fleet dashboard interface.

## 2. The Trip Form & Parameters (1.5 mins)
- **Action:** Fill out the origin and destination (e.g., Chicago, IL to Denver, CO).
- **Parameters:**
  - Departure Time: Highlight that this affects the weather forecast used.
  - Load Weight: Explain that lighter loads (e.g., 20,000 lbs) are more susceptible to wind and have stricter safety thresholds than heavy loads.
  - Checkpoint Interval: Show the 10/25/50 mile granularity selection.
- **Action:** Click "Find safest route". 

## 3. Route Comparison & Safety Logic (2 mins)
- **Visuals:** Show the generated route cards on the left panel.
- **Key metrics:** Point out distance, duration, and the risk summaries (No-Travel, Severe, High miles).
- **Recommendation Logic:** Explain why a route got the "⭐ Recommended" tag:
  - First priority: Minimize No-Travel conditions.
  - Second priority: Minimize Severe conditions.
  - Tie-breakers: High conditions -> Average risk -> Shortest travel time.
- **Safety Highlight:** Demonstrate the explicit "No Travel Warning" block if all routes are forced into No-Travel zones.

## 4. Map Experience & Checkpoint Details (2 mins)
- **Action:** Click between different route cards and watch the map highlight the selected route.
- **Checkpoints:** Hover/click on the colored dots along the route.
- **Details:** Explain that each dot shows the exact ETA and the forecasted weather at that precise moment. The risk level is calculated dynamically for that hour and load weight.

## 5. Time-Scrubber Heatmap (1.5 mins)
- **Feature:** Direct attention to the floating "Heatmap Forecast" slider at the bottom.
- **Action:** Drag the slider through the 0-48h range.
- **Explanation:** Show how the entire corridor's risk footprint shifts as storms move over time. Explain that this allows dispatchers to answer: "Should we leave now, or delay departure by 6 hours to let the storm pass?"
- **Performance note:** Mention how smoothly it updates without requiring a page reload or new API calls.

## 6. Architecture & Known Limitations (1.5 mins)
- **Architecture:** Briefly mention the decoupled Django backend (pure Python risk logic) and the React/Leaflet frontend.
- **Limitation 1 (Crucial):** Emphasize that the demo uses OSRM's public *car* profile. It does NOT route around low bridges or truck-restricted roads. In production, this must be swapped for a commercial truck router (like HERE or Mapbox).
- **Limitation 2:** ETA calculations assume constant driving without mandatory hours-of-service breaks.
- **Conclusion:** Wrap up and thank the viewer.
