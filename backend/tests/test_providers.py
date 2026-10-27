from unittest.mock import patch

from trips.providers import forecasts, geoapify_route, ors_routes, routes


def test_ors_normalization(monkeypatch):
    monkeypatch.setenv("ORS_API_KEY", "test-only")
    payload = {
        "features": [
            {
                "geometry": {"coordinates": [[0, 0], [1, 0]]},
                "properties": {
                    "summary": {"distance": 100, "duration": 20},
                    "segments": [{"steps": [{"way_points": [0, 1], "duration": 20}]}],
                },
            }
        ]
    }
    with patch("trips.providers.request_json", return_value=payload) as request:
        result = ors_routes([0, 0], [1, 0])[0]
    assert result["steps"] == [{"end": 1, "duration": 20}]
    assert request.call_args.kwargs["body"]["alternative_routes"]["target_count"] == 3
    assert "driving-hgv" in request.call_args.args[1]


def test_geoapify_normalization(monkeypatch):
    monkeypatch.setenv("GEOAPIFY_API_KEY", "test-only")
    payload = {
        "features": [
            {
                "geometry": {"type": "MultiLineString", "coordinates": [[[0, 0], [1, 0]], [[1, 0], [2, 0]]]},
                "properties": {
                    "distance": 100,
                    "time": 20,
                    "legs": [
                        {"steps": [{"to_index": 1, "time": 10}]},
                        {"steps": [{"to_index": 1, "time": 10}]},
                    ],
                },
            }
        ]
    }
    with patch("trips.providers.request_json", return_value=payload):
        result = geoapify_route([0, 0], [2, 0], "balanced")[0]
    assert result["coordinates"] == [[0, 0], [1, 0], [2, 0]]
    assert [s["end"] for s in result["steps"]] == [1, 2]


def test_long_route_skips_ors_and_deduplicates(road):
    with (
        patch("trips.providers.ors_routes") as ors,
        patch("trips.providers.geoapify_route", return_value=[road]),
    ):
        result, warnings = routes([0, 0], [2, 0])
    ors.assert_not_called()
    assert len(result) == 1 and "Only 1 distinct" in warnings[0]


def test_batch_deduplicates_locations():
    with patch("trips.providers.forecast_batch", return_value=[{"time": [0]}]) as batch:
        result, warnings = forecasts([[1, 2], [1.00001, 2]])
    batch.assert_called_once()
    assert len(result) == 1 and warnings == []
