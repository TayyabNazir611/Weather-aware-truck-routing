# 7–8 minute Loom outline

1. **0:00–0:45 — Problem and architecture.** Truck routes, checkpoint arrival-time weather, cargo rules; React/Vite frontend and stateless Django REST backend. Show the two-page assessment checklist.
2. **0:45–2:15 — Live trip.** Chicago → Merrillville, future departure, 35,000 lb, 10-mile spacing. Select autocomplete results. Explain genuine alternatives and the provider limitation. Show distances, drive times and the recommendation.
3. **2:15–3:15 — Checkpoints.** Select another route, inspect a map marker and table row. Show ETA, mph, rain/snow in/hr, exposure miles. Explain step-duration ETA interpolation and midpoint exposure attribution.
4. **3:15–4:15 — Corridor forecast.** Scrub 0→24→48 hours. Explain the overlay's sampled resolution, selected absolute time, and distinction from arrival-time route forecasts. Show the Network panel has no weather requests during scrubbing.
5. **4:15–5:15 — Rules.** Open `risk.py` and boundary tests. Explain precipitation endpoint interpretation, strict load thresholds, No Travel eligibility, Unknown handling and the lexicographic comparator.
6. **5:15–6:15 — Reliability.** Show tests and CI. Demonstrate a shorter/longer route and honest fewer-alternative messaging. Show explicit recorded demo labeling; explain it never masks live errors.
7. **6:15–7:30 — Deployment and limitations.** Vercel root config, DigitalOcean Docker/App spec, server-only secrets, noncommercial weather plan, truck-profile limitations and quota constraints. Finish on the actual hosted app when available.

Record only after the real production URLs are verified. Avoid showing `.env`, `env.txt`, account keys or secret settings. Use the recorded demo only if explicitly identified as a historical snapshot. A Loom recording has not been created by the agent.
