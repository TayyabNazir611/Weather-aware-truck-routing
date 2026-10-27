# Provider selection and evidence

Checked October 27, 2026 against official documentation and actual authenticated requests. Credentials were never written to reports or browser bundles.

| Provider | Capabilities and verified limits | Decision |
|---|---|---|
| openrouteservice | HGV routing and up to three alternative candidates. Live API rejected estimated alternative routes above **100,000 m**. The supplied account's response advertised `X-Ratelimit-Limit: 200`; the period was not established, so this is not claimed as a universal daily quota. | Try for short corridors, then supplement with Geoapify if practical deduplication leaves fewer than three. |
| Geoapify | Truck mode, step times/geometry; balanced, short and less_maneuvers preferences. Pricing page: **3,000 credits/day, up to 5 requests/sec**, no card for free signup. Free commercial use allowed with attribution and limits. Credits are not necessarily one per request. | Address autocomplete plus long-route and alternative-candidate truck routing. Three preferences do not guarantee three distinct routes. |
| Open-Meteo | Seven days by default; hourly wind, rain, showers, snowfall; multi-location requests. Free noncommercial service: **10,000 calls/day**, no uptime guarantee. Location/variable accounting can make a batch count as multiple calls. | Evaluation weather service. Normalize units and preserve missing values. |
| OpenFreeMap | Public MapLibre styles including Positron, sourced from OpenStreetMap/OpenMapTiles; no browser API key required for this integration. | Basemap; retain the built-in attribution. No public OSM tile or Nominatim endpoint is used. |

Official references:

- [Geoapify developer documentation supplied by the user](https://apidocs.geoapify.com/docs)
- [Geoapify routing](https://apidocs.geoapify.com/docs/routing/)
- [Geoapify pricing and usage terms](https://www.geoapify.com/pricing/)
- [openrouteservice API portal](https://api.openrouteservice.org/)
- [Open-Meteo forecast variables and units](https://open-meteo.com/en/docs)
- [Open-Meteo pricing and licensing](https://open-meteo.com/en/pricing)
- [OpenFreeMap integration and attribution](https://openfreemap.org/quick_start/)

## Actual capability probes

Chicago `[-87.6298,41.8781]` → Merrillville `[-87.3311,41.4731]`:

1. ORS returned three HGV candidates of 73,143.0 / 69,076.8 / 69,076.9 meters.
2. Geometry comparison discarded the practically identical final candidate.
3. Geoapify preferences supplied a third distinct route (balanced: 69,376 m).
4. Full live analysis returned three routes, complete weather, a recommendation, and 49 corridor frames.

Chicago → Indianapolis: Geoapify returned **two** distinct routes after deduplication, approximately 183.4 and 177.2 miles. The application reports the shortfall. Calling ORS alternatives for this corridor returned HTTP 400, code 2004, with the 100 km restriction. This is why the app does not assume HGV alternatives work for arbitrary cross-state distances.

Deduplication compares 101 normalized-progress samples per route: candidates with at least 96 samples within 500 m are treated as practically identical. This is a documented heuristic, not a claim of topological route equivalence.

## Forecast semantics

Hourly precipitation is an accumulation over the preceding hour; conversion to an average per-hour rate is valid for that interval. Snow is snowfall depth, not liquid-equivalent precipitation. Rain includes convective showers. Higher-resolution 15-minute data is available for some regions, but this version uses globally consistent hourly fields. Brief hazards within an hour may be smoothed out. Forecast data is attributed to Open-Meteo under CC BY 4.0.

## DigitalOcean verification

The official [App Platform pricing](https://www.digitalocean.com/pricing/app-platform) page lists paid services starting at **$5/month**. The free tier is static hosting and does not run Django. The supplied app spec targets the smallest paid service; confirm the estimate at creation, especially transfer allowances and any selected upgrades.

**No promotional credit is assumed.** The historical free-trial URL redirected to the general DigitalOcean page during this check, and other historical trial links returned 404. We could not verify a current signup-credit amount, duration, eligibility, or coverage of App Platform. Those account-specific terms must be checked in signup before relying on them. A payment method may undergo preauthorization; active resources can be billed after any credit expires. No billing account was connected and no resources were provisioned.

The architecture is also portable to another Docker-capable host. DigitalOcean remains the requested target; choosing another provider based on an unverified free offer would not improve deployment certainty.
