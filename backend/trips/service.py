from datetime import timedelta

from . import providers
from .geometry import METERS_PER_MILE, corridor, sample
from .risk import aggregate, rank
from .weather import at_time


def analyze_trip(data):
    raw, warnings = providers.routes(data["origin"]["coordinates"], data["destination"]["coordinates"])
    departure, load = data["departure"], data["load_lb"]
    grid, spacing = corridor(raw)
    samples = [sample(route, data["interval_miles"]) for route in raw]
    count = sum(map(len, samples))
    if count > 1000:
        raise providers.ProviderError(
            "This trip exceeds 1,000 checkpoints. Choose a larger sampling interval.", 422
        )
    points = [p["coordinates"] for route in samples for p in route] + grid
    weather, failures = providers.forecasts(points)
    warnings.extend(failures)

    def lookup(point):
        return weather.get(tuple(round(v, 3) for v in point))

    routes = []
    for i, (route, checkpoints) in enumerate(zip(raw, samples)):
        for j, point in enumerate(checkpoints):
            eta = departure + timedelta(seconds=point.pop("seconds"))
            forecast = at_time(lookup(point["coordinates"]), eta.timestamp(), load)
            point.update(
                id=f"r{i + 1}-c{j}",
                eta=eta.isoformat(),
                weather=forecast,
                risk=forecast["risk"] if forecast else None,
            )
        miles = route["distance_meters"] / METERS_PER_MILE
        routes.append(
            {
                "id": f"r{i + 1}",
                "name": f"Route {i + 1}",
                "provider": route["provider"],
                "geometry": {"type": "LineString", "coordinates": route["coordinates"]},
                "distance_miles": miles,
                "duration_seconds": route["duration_seconds"],
                "arrival": (departure + timedelta(seconds=route["duration_seconds"])).isoformat(),
                "checkpoints": checkpoints,
                "summary": aggregate(checkpoints, miles),
            }
        )
    routes, recommended, explanation = rank(routes)
    base = providers.utc_now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    times = [(base + timedelta(hours=h)).isoformat() for h in range(49)]
    heatmap = []
    for point in grid:
        values = [at_time(lookup(point), (base + timedelta(hours=h)).timestamp(), load) for h in range(49)]
        heatmap.append({"coordinates": point, "risk": [v["risk"] if v else None for v in values]})
    if any(not r["summary"]["eligible"] and r["summary"]["counts"]["Unknown"] for r in routes):
        warnings.append(
            "Some checkpoint forecasts are unavailable. Affected routes are not eligible for recommendation."
        )
    return {
        "routes": routes,
        "recommended_id": recommended,
        "explanation": explanation,
        "warnings": list(dict.fromkeys(warnings)),
        "mode": "live",
        "departure": departure.isoformat(),
        "load_lb": load,
        "interval_miles": data["interval_miles"],
        "heatmap": {"times": times, "points": heatmap, "spacing_miles": spacing},
        "attribution": "Routing: openrouteservice / Geoapify © OpenStreetMap contributors. Weather: Open-Meteo (CC BY 4.0).",
        "limitations": "Truck profile uses provider defaults; cargo weight is only used for weather rules. Verify vehicle dimensions, gross weight, road restrictions and rest stops separately.",
    }
