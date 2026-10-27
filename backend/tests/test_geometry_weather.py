import pytest
from trips.geometry import METERS_PER_MILE, corridor, deduplicate, distance, sample
from trips.weather import at_time


def test_distance_and_step_eta(road):
    assert distance([0, 0], [1, 0]) == pytest.approx(111195, rel=0.001)
    points = sample(road, 25)
    assert [p["mile"] for p in points] == pytest.approx([0, 25, 50, 75, 100])
    assert [p["seconds"] for p in points] == pytest.approx([0, 900, 1800, 4500, 7200])
    assert points[1]["coordinates"] == pytest.approx([0.25, 0])


def test_short_route_endpoint_and_geometry_bend(road):
    road["distance_meters"] = METERS_PER_MILE
    road["coordinates"] = [[0, 0], [0, 1], [1, 1]]
    points = sample(road, 10)
    assert len(points) == 2
    assert points[-1]["coordinates"] == [1, 1]


def test_duplicates_and_corridor_bound(road):
    assert len(deduplicate([road, road])) == 1
    points, spacing = corridor([road])
    assert 0 < len(points) <= 100
    assert spacing >= 25


def test_degenerate_route(road):
    road["coordinates"] = [[0, 0], [0, 0]]
    with pytest.raises(ValueError):
        sample(road, 10)


def series():
    return {
        "time": [0, 3600, 7200],
        "wind_speed_10m": [10, 30, 50],
        "rain": [0, 2.54, 0],
        "showers": [0, 2.54, 0],
        "snowfall": [0, 2.54, 0],
    }


def test_precipitation_interval_and_wind_interpolation():
    result = at_time(series(), 1800, 0)
    assert result["wind_mph"] == 20
    assert result["rain_in_hr"] == pytest.approx(0.2)
    assert result["snow_in_hr"] == 1
    assert result["interval_end"] == 3600
    assert result["risk"] == 2
    assert at_time(series(), 3600, 0)["rain_in_hr"] == pytest.approx(0.2)
    assert at_time(series(), 3601, 0)["rain_in_hr"] == 0


def test_missing_and_outside_window():
    for time in (-1, 7201):
        assert at_time(series(), time, 0) is None
    data = series()
    data["rain"][1] = None
    assert at_time(data, 1800, 0) is None
    assert at_time(None, 1800, 0) is None
