"""External APIs terminate here; business logic only sees normalized objects."""

import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import requests
from django.core.cache import cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .geometry import deduplicate, distance


class ProviderError(Exception):
    def __init__(self, message, status=502):
        self.message, self.status = message, status
        super().__init__(message)


def request_json(provider: str, url: str, *, params=None, body=None, headers=None, ttl=900):
    # Hash the full request, including credentials, without ever logging them.
    key = hashlib.sha256(json.dumps([url, params, body, headers], sort_keys=True).encode()).hexdigest()
    saved = cache.get(key)
    if saved is not None:
        return saved
    with requests.Session() as session:
        retry = Retry(
            total=1,
            backoff_factor=0.3,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET", "POST"],
            respect_retry_after_header=False,
        )
        session.mount("https://", HTTPAdapter(max_retries=retry))
        try:
            response = session.request(
                "POST" if body else "GET", url, params=params, json=body, headers=headers, timeout=(5, 25)
            )
            if response.status_code == 429:
                raise ProviderError(f"{provider} quota reached. Please wait before trying again.", 503)
            if response.status_code in (401, 403):
                raise ProviderError(f"{provider} credentials were rejected. Check server configuration.", 503)
            if response.status_code >= 400:
                raise ProviderError(
                    f"{provider} could not fulfill this request (HTTP {response.status_code}). Try a shorter trip or different locations."
                )
            data = response.json()
        except (requests.RequestException, ValueError):
            raise ProviderError(
                f"{provider} is unavailable or returned invalid data. Please try again.", 503
            ) from None
    cache.set(key, data, ttl)
    return data


def credential(name):
    key = os.getenv(name)
    if not key:
        raise ProviderError(f"Server configuration is missing {name}.", 503)
    return key


def locations(query):
    data = request_json(
        "Geoapify",
        "https://api.geoapify.com/v1/geocode/autocomplete",
        params={
            "text": query,
            "format": "json",
            "limit": 5,
            "filter": "countrycode:us",
            "apiKey": credential("GEOAPIFY_API_KEY"),
        },
        ttl=86400,
    )
    return [{"label": p["formatted"], "coordinates": [p["lon"], p["lat"]]} for p in data.get("results", [])]


def ors_routes(origin, destination):
    data = request_json(
        "openrouteservice",
        "https://api.openrouteservice.org/v2/directions/driving-hgv/geojson",
        body={
            "coordinates": [origin, destination],
            "alternative_routes": {"target_count": 3, "share_factor": 0.8, "weight_factor": 1.8},
            "instructions": True,
        },
        headers={"Authorization": credential("ORS_API_KEY")},
    )
    routes = []
    for feature in data.get("features", []):
        p = feature["properties"]
        routes.append(
            {
                "coordinates": feature["geometry"]["coordinates"],
                "distance_meters": p["summary"]["distance"],
                "duration_seconds": p["summary"]["duration"],
                "provider": "openrouteservice HGV",
                "steps": [
                    {"end": step["way_points"][1], "duration": step["duration"]}
                    for leg in p["segments"]
                    for step in leg["steps"]
                ],
            }
        )
    return routes


def geoapify_route(origin, destination, preference):
    data = request_json(
        "Geoapify",
        "https://api.geoapify.com/v1/routing",
        params={
            "waypoints": "|".join(f"{lat},{lon}" for lon, lat in [origin, destination]),
            "mode": "truck",
            "type": preference,
            "units": "metric",
            "apiKey": credential("GEOAPIFY_API_KEY"),
        },
    )
    routes = []
    for f in data.get("features", []):
        p = f["properties"]
        lines = (
            f["geometry"]["coordinates"]
            if f["geometry"]["type"] == "MultiLineString"
            else [f["geometry"]["coordinates"]]
        )
        coords, steps = [], []
        for i, line in enumerate(lines):
            offset = len(coords) - (1 if coords else 0)
            coords.extend(line[1:] if coords else line)
            for step in p["legs"][i].get("steps", []):
                steps.append({"end": offset + step["to_index"], "duration": step["time"]})
        routes.append(
            {
                "coordinates": coords,
                "distance_meters": p["distance"],
                "duration_seconds": p["time"],
                "provider": f"Geoapify truck / {preference}",
                "steps": steps,
            }
        )
    return routes


def routes(origin, destination):
    results, warnings = [], []
    # Hosted ORS alternative routes have a 100 km limit. Geoapify handles longer trips.
    if distance(origin, destination) < 80000:
        try:
            results.extend(ors_routes(origin, destination))
        except ProviderError as e:
            warnings.append(e.message)
    if len(deduplicate(results)) < 3:
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [
                pool.submit(geoapify_route, origin, destination, kind)
                for kind in ("balanced", "short", "less_maneuvers")
            ]
            for future in futures:
                try:
                    results.extend(future.result())
                except ProviderError as e:
                    warnings.append(e.message)
    unique = deduplicate(results)[:3]
    if not unique:
        raise ProviderError(warnings[0] if warnings else "No truck routes found for these locations.", 422)
    if len(unique) < 3:
        warnings.append(
            f"Only {len(unique)} distinct truck route(s) were available. Duplicate candidates were removed."
        )
    return unique, warnings


def forecast_batch(points):
    data = request_json(
        "Open-Meteo",
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": ",".join(str(p[1]) for p in points),
            "longitude": ",".join(str(p[0]) for p in points),
            "hourly": "wind_speed_10m,rain,showers,snowfall",
            "wind_speed_unit": "mph",
            "precipitation_unit": "mm",
            "timezone": "GMT",
            "timeformat": "unixtime",
            "forecast_days": 7,
        },
    )
    items = data if isinstance(data, list) else [data]
    if len(items) != len(points):
        raise ProviderError("Open-Meteo returned an incomplete location batch.")
    result = []
    for item in items:
        units = item.get("hourly_units", {})
        if any(
            units.get(k) != v
            for k, v in {"wind_speed_10m": "mp/h", "rain": "mm", "showers": "mm", "snowfall": "cm"}.items()
        ):
            raise ProviderError("Open-Meteo returned unexpected units; forecasts were not classified.")
        result.append(item.get("hourly", {}))
    return result


def forecasts(points):
    """Deduplicate co-located samples and bound concurrency to two batches."""
    unique = list(dict.fromkeys((round(p[0], 3), round(p[1], 3)) for p in points))
    batches = [unique[i : i + 25] for i in range(0, len(unique), 25)]
    result, warnings = {}, []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(forecast_batch, batch) for batch in batches]
        for batch, future in zip(batches, futures):
            try:
                result.update(zip(batch, future.result()))
            except ProviderError as e:
                warnings.append(e.message)
                result.update((p, None) for p in batch)
    return result, list(dict.fromkeys(warnings))


def utc_now():
    return datetime.now(UTC)
