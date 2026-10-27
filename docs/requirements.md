# Assessment specification and implementation plan

Source: both pages of `fs-assessment-spotter.pdf`, the supplied engineering brief, and the user's manually verified table.

## Required behavior

- React + TypeScript + Vite frontend; Django REST backend.
- Origin/destination search, departure datetime, load in pounds, 10/25/50-mile sampling.
- Request three genuine routes; deduplicate and disclose when fewer exist.
- Follow route geometry; use provider step durations for checkpoint ETAs.
- Forecast wind, rain, snow at each checkpoint ETA, with normalized units.
- Show route geometry, checkpoint details, ETA, exposure miles, risk counts and summaries.
- Rank eligible routes lexicographically by Severe miles, High miles, distance-weighted mean risk, driving time.
- Independent corridor forecast heatmap with 0–48-hour slider; never alter trip ranking when scrubbing.
- Loading, errors, missing data, responsive layout, accessible controls.
- Automated domain, API, component and browser tests; reproducible explicitly labeled demonstration.
- GitHub-ready repository, Vercel frontend, DigitalOcean backend, walkthrough outline.

## Exact interpretation

Wind: [0,25) Low, [25,35) Moderate, [35,45) High, [45,55) Severe, [55,infinity) No Travel.
Rain: [0,.10) Low, [.10,.25) Moderate, [.25,.50) High, [.50,1.00] Severe, >1.00 No Travel.
Snow: [0,.5) Low, [.5,1) Moderate, [1,2) High, [2,3] Severe, >3 No Travel.
Overlapping internal rain/snow endpoints enter the higher class. Fractional wind values use continuous bands.
Wind [45,55) and load >30,000 lb becomes No Travel; wind [35,45) and load >40,000 lb becomes Severe. Equality at the load thresholds does not trigger the override.
Highest hazard wins. Missing data is Unknown, never Low. A route with any No Travel checkpoint or missing forecast is ineligible. No recommendation if all are ineligible.

Risk scores are 0/1/2/3/4. Exposure uses nearest-checkpoint attribution: each checkpoint owns the interval between adjacent distance midpoints. This conserves total route miles for every sampling interval. Sampling can still miss small weather features; resolution changes are not guaranteed to yield identical estimates.
Rain and convective showers are added, in mm per preceding hour, then divided by 25.4. Snowfall is depth in cm per preceding hour, divided by 2.54. Select the forecast interval ending at ceil(ETA to hour); wind is linearly interpolated between surrounding hourly instants. No extrapolation beyond available forecasts.
All API timestamps are UTC; the form labels the browser timezone. Driving times exclude rest stops and traffic unless the provider explicitly supports them. Load is cargo weight, not gross vehicle weight, so it is used for weather rules only.

## Dependency-ordered plan

1. Verify provider documentation and live HGV alternatives; record actual results.
2. Implement pure risk, geometry/ETA sampling, exposure and ranking with boundary tests.
3. Implement timeouts/retries, cached provider adapters, batch weather and validated REST API.
4. Build map-led trip planner, comparison and checkpoint inspection.
5. Add bounded corridor grid time series and client-only forecast scrubbing.
6. Execute domain/API/UI/E2E checks and production build; inspect desktop/mobile UI.
7. Prepare Git integration, deployment configuration, setup and walkthrough documentation.

## Principal risks

Hosted HGV alternative routing may limit route length and number of alternatives. Provider data is not a legal truck-clearance guarantee. Weather forecasts have limited horizon and spatial resolution. Public demo APIs have quotas; batching still consumes location-based quota. Secret files must stay ignored. Paid hosting and account-specific credits require separate verification before provisioning.
