"""Pure assessment rules. Unknown is deliberately separate from numeric risk."""

import math

LEVELS = ["Low", "Moderate", "High", "Severe", "No Travel"]


def classify(wind: float, rain: float, snow: float, load: float) -> int:
    if any(not math.isfinite(x) or x < 0 for x in (wind, rain, snow, load)):
        raise ValueError("Weather and load must be finite, nonnegative numbers.")
    w = sum(wind >= edge for edge in (25, 35, 45, 55))
    r = 4 if rain > 1 else sum(rain >= edge for edge in (0.1, 0.25, 0.5))
    s = 4 if snow > 3 else sum(snow >= edge for edge in (0.5, 1, 2))
    if wind >= 45 and load > 30000:
        w = 4
    elif wind >= 35 and load > 40000:
        w = max(w, 3)
    return max(w, r, s)


def aggregate(checkpoints: list[dict], miles: float) -> dict:
    exposure = {name: 0.0 for name in [*LEVELS, "Unknown"]}
    counts = {name: 0 for name in exposure}
    for i, point in enumerate(checkpoints):
        left = 0 if i == 0 else (checkpoints[i - 1]["mile"] + point["mile"]) / 2
        right = miles if i == len(checkpoints) - 1 else (point["mile"] + checkpoints[i + 1]["mile"]) / 2
        label = "Unknown" if point["risk"] is None else LEVELS[point["risk"]]
        point["exposure_miles"] = max(0, right - left)
        exposure[label] += point["exposure_miles"]
        counts[label] += 1
    known = miles - exposure["Unknown"]
    average = sum(exposure[name] * i for i, name in enumerate(LEVELS)) / known if known > 0 else None
    return {
        "exposure": exposure,
        "counts": counts,
        "average_risk": average,
        "max_risk": max((p["risk"] for p in checkpoints if p["risk"] is not None), default=None),
        "eligible": counts["Unknown"] == 0 and counts["No Travel"] == 0,
    }


def rank(routes: list[dict]) -> tuple[list[dict], str | None, str]:
    def key(r):
        s = r["summary"]
        return (
            not s["eligible"],
            s["exposure"]["Severe"],
            s["exposure"]["High"],
            s["average_risk"] if s["average_risk"] is not None else float("inf"),
            r["duration_seconds"],
            r["id"],
        )

    ordered = sorted(routes, key=key)
    for i, route in enumerate(ordered):
        route["rank"] = i + 1
    best = next((r for r in ordered if r["summary"]["eligible"]), None)
    if not best:
        return (
            ordered,
            None,
            "No route can be recommended: every option has No Travel conditions or unavailable forecasts.",
        )
    s = best["summary"]
    explanation = (
        f"{best['name']} ranks first among eligible routes: {s['exposure']['Severe']:.1f} Severe miles, "
        f"{s['exposure']['High']:.1f} High miles, {s['average_risk']:.2f}/4 average risk, "
        f"{best['duration_seconds'] / 60:.0f} minutes. Compared in that priority order."
    )
    return ordered, best["id"], explanation
