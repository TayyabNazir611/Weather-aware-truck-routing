# Verification evidence — October 27, 2026

User story: selected trip inputs → React HTTP request → Django validation → live truck routes → ETA-matched Open-Meteo forecasts → risk/exposure/ranking → interactive MapLibre map and independent forecast timeline.

## Executed checks

| Check | Result | Evidence |
|---|---|---|
| Backend unit/integration suite | 62 tests passed | `python -m pytest backend -q`; risk thresholds, strict load boundaries, geometry/step ETA, exposure conservation, recommendation order, forecast intervals, conversions, missing fields, adapters, caching, timeout/quota handling, API validation |
| Frontend tests | 4 tests passed | `npm test`; form validation, demo/selection, slider action, source synchronization and stable map lifetime |
| Browser journeys | 6 tests passed | `npm run test:e2e`; form→REST response, 10/50-mile choice, provider error, route selection, checkpoint inspection, slider, no scrub requests, map canvas, responsive 320/375/414/768 |
| Python lint/format | Passed | `ruff check backend`, `ruff format --check backend` |
| Frontend lint | Passed | `npm run lint` |
| TypeScript + production bundle | Passed | `npm run build` |
| Built frontend browser smoke test | Passed | `node scripts/verify-production.mjs`; 618-pixel map canvas, 3 route cards, no JS errors; [screenshot](screenshots/production-build.png) |
| Dependency audit | Zero reported vulnerabilities | `npm audit` after updating MapLibre and Vitest |
| Django configuration | Passed | `python backend/manage.py check` |
| Live provider probe | Three distinct routes | Chicago→Merrillville with ORS HGV + Geoapify truck; duplicates removed |
| Long-route probe | Two distinct routes, disclosed | Chicago→Indianapolis, Geoapify truck preferences |
| Live browser workflow | HTTP 200; 3 routes, 6 checkpoints each, 49 frames; zero warnings and JS errors | [Machine-readable report](live-verification.json), [screenshot](screenshots/live-desktop.png) |
| Secret exclusion | Passed | `git check-ignore` lists `backend/.env` and `env.txt`; exact supplied-key scan found no values in publishable files |

The browser suite mocks provider responses and the basemap style for determinism; it still runs the real WebGL map, workers, GeoJSON sources, React form, and HTTP request handling. The separate opt-in live check uses the real Django server, credentials, geocoding, routing, forecasts, and public basemap. These are different evidence sources, not a claim that mocked browser tests alone verify provider integration.

## Visual inspection

Rendered and reviewed both assessment PDF pages. Inspected the live desktop map and narrow mobile output after worker and lazy-CSS fixes. Real-map screenshots at [320](screenshots/live-map-320.png), [375](screenshots/live-map-375.png), [414](screenshots/live-map-414.png), and [768 pixels](screenshots/live-map-768.png) have no horizontal page overflow. Map attribution is preserved. At small widths the planner and map stack vertically; the checkpoint table scrolls horizontally within its container.

## Issues discovered and repaired

- Two ORS candidates differed by only 0.1 meter: practical geometry deduplication prevents three-card duplication.
- Initial library ranges included reported security advisories: updated MapLibre to 6.16 and Vitest to 5.0; audit returned zero vulnerabilities.
- MapLibre 6's worker initially resolved incorrectly through Vite: imported the worker with `?worker&url` and configured `setWorkerUrl`.
- Lazy-loaded MapLibre CSS initially overrode map positioning: an explicit higher-specificity container rule now preserves map dimensions. Browser assertions include actual canvas visibility/height.
- Editing trip inputs could leave prior results displayed: changing inputs now clears old results. Browser cancellation suppresses stale responses, including demo fetches.
- Generic `summary` test selector also matched map attribution: scoped checkpoint-table selectors to the route detail panel.

## Performance and limitations

The form bundle is approximately 76.5 kB gzip. The lazy map vendor chunk is approximately 290.9 kB gzip; its worker is about 517 kB uncompressed. Vite emits a large-chunk advisory for the map library. This is disclosed, not treated as a failed build. There is one map instance per mount, memoized provider data, bounded batch concurrency, and local source updates on timeline changes. No browser FPS or production load-test claim is made.

Local checks do not establish production uptime or remote deployment correctness. Docker image execution, GitHub-hosted CI, paid DigitalOcean provisioning, Vercel production deployment and the Loom recording have not been performed. The exact post-deployment smoke test is in [deployment.md](deployment.md).

## Requirements compliance

- [x] Assessment pages read and requirements/ambiguities documented.
- [x] React/TypeScript/Vite frontend, Django/DRF backend.
- [x] Trip inputs, location autocomplete, UTC processing, explicit browser timezone.
- [x] Genuine truck route candidates, deduplication and honest fewer-route messages.
- [x] 10/25/50-mile geometry sampling, checkpoint ETA and arrival-time forecasts.
- [x] Exact hazard/load rules, Unknown and No Travel handling.
- [x] Distance-aware exposure and deterministic prescribed ranking.
- [x] Map routes, checkpoint risk/detail inspection, ETA and route summaries.
- [x] Corridor risk overlay, legend and independent 0–48-hour timeline.
- [x] Loading, cancellation, error, empty, live and recorded-demo states.
- [x] Automated tests, responsive checks and production frontend build.
- [x] Vercel configuration, DigitalOcean template, environment examples, CI and walkthrough outline.
- [ ] Publish/select the remote GitHub repository.
- [ ] Connect and deploy the frontend/backend accounts; verify production URLs.
- [ ] Record and submit the Loom walkthrough.
