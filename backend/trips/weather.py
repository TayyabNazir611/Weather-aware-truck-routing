from bisect import bisect_left
from math import isfinite

from .risk import classify


def at_time(series: dict | None, timestamp: float, load: float) -> dict | None:
    if not series or not series.get("time"):
        return None
    times = series["time"]
    i = bisect_left(times, timestamp)
    if i >= len(times) or timestamp < times[0]:
        return None
    j = max(0, i - 1)
    try:
        values = [series[name][i] for name in ["wind_speed_10m", "rain", "showers", "snowfall"]]
        previous_wind = series["wind_speed_10m"][j]
        if any(x is None or not isfinite(x) or x < 0 for x in [*values, previous_wind]):
            return None
        fraction = (timestamp - times[j]) / (times[i] - times[j]) if i != j else 0
        wind = previous_wind + (values[0] - previous_wind) * fraction
        rain = (values[1] + values[2]) / 25.4
        snow = values[3] / 2.54
        return {
            "wind_mph": wind,
            "rain_in_hr": rain,
            "snow_in_hr": snow,
            "risk": classify(wind, rain, snow, load),
            "interval_end": times[i],
        }
    except (KeyError, IndexError, TypeError):
        return None
