from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()


@pytest.fixture
def trip():
    return {
        "origin": {"label": "Chicago", "coordinates": [-87.63, 41.88]},
        "destination": {"label": "Gary", "coordinates": [-87.33, 41.47]},
        "departure": (timezone.now() + timedelta(hours=2)).isoformat(),
        "load_lb": 35000,
        "interval_miles": 25,
    }


@pytest.fixture
def road():
    return {
        "coordinates": [[0, 0], [0.5, 0], [1, 0]],
        "distance_meters": 100 * 1609.344,
        "duration_seconds": 7200,
        "steps": [{"end": 1, "duration": 1800}, {"end": 2, "duration": 5400}],
        "provider": "test",
    }
