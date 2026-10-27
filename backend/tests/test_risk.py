import math

import pytest
from trips.risk import aggregate, classify, rank


@pytest.mark.parametrize(
    "value,expected",
    [(24.999, 0), (25, 1), (34.999, 1), (35, 2), (44.999, 2), (45, 3), (54.999, 3), (55, 4), (55.001, 4)],
)
def test_wind_boundaries(value, expected):
    assert classify(value, 0, 0, 0) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (0.0999, 0),
        (0.1, 1),
        (0.1001, 1),
        (0.2499, 1),
        (0.25, 2),
        (0.2501, 2),
        (0.4999, 2),
        (0.5, 3),
        (0.5001, 3),
        (1, 3),
        (1.0001, 4),
    ],
)
def test_rain_boundaries(value, expected):
    assert classify(0, value, 0, 0) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (0.4999, 0),
        (0.5, 1),
        (0.5001, 1),
        (0.9999, 1),
        (1, 2),
        (1.0001, 2),
        (1.9999, 2),
        (2, 3),
        (2.0001, 3),
        (3, 3),
        (3.0001, 4),
    ],
)
def test_snow_boundaries(value, expected):
    assert classify(0, 0, value, 0) == expected


@pytest.mark.parametrize(
    "wind,load,expected",
    [(45, 30000, 3), (45, 30000.1, 4), (35, 40000, 2), (35, 40000.1, 3), (34.99, 50000, 1), (55, 0, 4)],
)
def test_load_boundaries(wind, load, expected):
    assert classify(wind, 0, 0, load) == expected


def test_highest_hazard_and_invalid_values():
    assert classify(30, 0.6, 0, 50000) == 3
    assert classify(40, 1.1, 4, 40001) == 4
    for invalid in [-1, math.nan, math.inf]:
        with pytest.raises(ValueError):
            classify(invalid, 0, 0, 0)


@pytest.mark.parametrize("interval", [10, 25, 50])
def test_exposure_conservation(interval):
    points = [{"mile": m, "risk": 2} for m in range(0, 101, interval)] + [{"mile": 105, "risk": 2}]
    s = aggregate(points, 105)
    assert sum(s["exposure"].values()) == pytest.approx(105)
    assert s["exposure"]["High"] == pytest.approx(105)
    assert s["average_risk"] == 2


def test_midpoint_exposure_and_missing():
    points = [{"mile": 0, "risk": 0}, {"mile": 25, "risk": 3}, {"mile": 30, "risk": None}]
    s = aggregate(points, 30)
    assert s["exposure"] == {
        "Low": 12.5,
        "Moderate": 0,
        "High": 0,
        "Severe": 15,
        "No Travel": 0,
        "Unknown": 2.5,
    }
    assert not s["eligible"]


def option(id, severe=0, high=0, avg=0, duration=100, eligible=True):
    return {
        "id": id,
        "name": id,
        "duration_seconds": duration,
        "summary": {"eligible": eligible, "exposure": {"Severe": severe, "High": high}, "average_risk": avg},
    }


def test_ranking_is_lexicographic():
    routes = [
        option("severe", severe=1),
        option("high", high=1),
        option("average", avg=1),
        option("slow", duration=110),
        option("best"),
        option("blocked", eligible=False, duration=1),
    ]
    ordered, best, explanation = rank(routes)
    assert [r["id"] for r in ordered] == ["best", "slow", "average", "high", "severe", "blocked"]
    assert best == "best" and "0.0 Severe miles" in explanation


def test_all_blocked_and_stable_tie():
    assert rank([option("blocked", eligible=False)])[1] is None
    assert rank([option("b"), option("a")])[1] == "a"
