"""Geometry-distance sampling with step-duration interpolation."""

from bisect import bisect_right
from math import asin, cos, radians, sin, sqrt

METERS_PER_MILE = 1609.344


def distance(a, b) -> float:
    lon1, lat1, lon2, lat2 = map(radians, [*a[:2], *b[:2]])
    h = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 6371008.8 * 2 * asin(min(1, sqrt(h)))


def cumulative(coords) -> list[float]:
    result = [0.0]
    for a, b in zip(coords, coords[1:]):
        result.append(result[-1] + distance(a, b))
    return result


def point_at(coords, distances, target):
    index = min(max(0, bisect_right(distances, target) - 1), len(coords) - 2)
    length = distances[index + 1] - distances[index]
    fraction = (target - distances[index]) / length if length else 0
    return [coords[index][j] + fraction * (coords[index + 1][j] - coords[index][j]) for j in (0, 1)]


def sample(route: dict, interval: int) -> list[dict]:
    coords, total = route["coordinates"], route["distance_meters"]
    distances = cumulative(coords)
    if len(coords) < 2 or distances[-1] <= 0 or total <= 0:
        raise ValueError("Route geometry has no usable length.")
    # Scale polyline distance to the provider's authoritative road distance.
    distances = [d * total / distances[-1] for d in distances]
    timing = [(0.0, 0.0)]
    elapsed = 0.0
    for step in route.get("steps", []):
        elapsed += step["duration"]
        end = min(step["end"], len(coords) - 1)
        if distances[end] > timing[-1][0]:
            timing.append((distances[end], elapsed))
    if len(timing) < 2:
        timing = [(0.0, 0.0), (total, route["duration_seconds"])]
    else:
        if timing[-1][0] < total:
            timing.append((total, route["duration_seconds"]))
        factor = route["duration_seconds"] / timing[-1][1] if timing[-1][1] else 1
        timing = [(d, t * factor) for d, t in timing]
    targets = [i * interval * METERS_PER_MILE for i in range(int(total / (interval * METERS_PER_MILE)) + 1)]
    if total - targets[-1] > 0.01:
        targets.append(total)
    else:
        targets[-1] = total
    result = []
    for target in targets:
        j = min(max(0, bisect_right([p[0] for p in timing], target) - 1), len(timing) - 2)
        d0, t0 = timing[j]
        d1, t1 = timing[j + 1]
        seconds = t0 + (t1 - t0) * (target - d0) / (d1 - d0)
        result.append(
            {
                "coordinates": point_at(coords, distances, target),
                "mile": target / METERS_PER_MILE,
                "seconds": seconds,
            }
        )
    return result


def deduplicate(routes: list[dict]) -> list[dict]:
    accepted = []
    signatures = []
    for route in routes:
        coords = route["coordinates"]
        distances = cumulative(coords)
        signature = [point_at(coords, distances, distances[-1] * i / 100) for i in range(101)]
        # Practical duplicates: at least 95% of normalized progress samples within 500 m.
        if any(sum(distance(a, b) < 500 for a, b in zip(signature, other)) >= 96 for other in signatures):
            continue
        signatures.append(signature)
        accepted.append(route)
    return accepted


def corridor(routes: list[dict], max_points=100) -> tuple[list[list[float]], float]:
    """Along-corridor lattice, 25-mile longitudinal and ~15-mile lateral spacing."""
    spacing = 25
    while True:
        cells = {}
        for route in routes:
            for p in sample(route, spacing):
                lon, lat = p["coordinates"]
                for delta in (-0.22, 0, 0.22):
                    key = (round(lon / 0.22), round((lat + delta) / 0.22))
                    cells[key] = [key[0] * 0.22, key[1] * 0.22]
        if len(cells) <= max_points or spacing >= 1600:
            return list(cells.values())[:max_points], spacing
        spacing *= 2
