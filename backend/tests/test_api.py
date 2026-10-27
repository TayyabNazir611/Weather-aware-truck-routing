from unittest.mock import patch

from rest_framework.test import APIClient
from trips.providers import ProviderError, forecast_batch, request_json


def test_health_and_validation(trip):
    client = APIClient()
    assert client.get("/api/health/").json() == {"status": "ok"}
    assert client.post("/api/routes/analyze/", {}, format="json").status_code == 400
    trip["destination"] = trip["origin"]
    assert client.post("/api/routes/analyze/", trip, format="json").status_code == 400


def test_timezone_required(trip):
    trip["departure"] = trip["departure"][:19]
    response = APIClient().post("/api/routes/analyze/", trip, format="json")
    assert response.status_code == 400
    assert "timezone" in str(response.json())


def test_provider_failure_is_sanitized(trip):
    with patch("trips.service.providers.routes", side_effect=ProviderError("Routing quota reached", 503)):
        response = APIClient().post("/api/routes/analyze/", trip, format="json")
    assert response.status_code == 503
    assert response.json()["error"]["message"] == "Routing quota reached"


def test_partial_weather_api_contract(trip, road):
    with (
        patch("trips.service.providers.routes", return_value=([road], [])),
        patch("trips.service.providers.forecasts", return_value=({}, ["Forecast unavailable"])),
    ):
        response = APIClient().post("/api/routes/analyze/", trip, format="json")
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_id"] is None
    assert data["routes"][0]["summary"]["exposure"]["Unknown"] == 100
    assert len(data["heatmap"]["times"]) == 49
    assert all(p["risk"] == [None] * 49 for p in data["heatmap"]["points"])


def test_search_validation_and_results():
    client = APIClient()
    assert client.get("/api/locations/search/?q=a").status_code == 400
    with patch("trips.providers.locations", return_value=[{"label": "Chicago", "coordinates": [-87, 41]}]):
        assert len(client.get("/api/locations/search/?q=Chicago").json()["results"]) == 1


def test_rate_limit_and_timeout():
    import pytest
    import requests

    with patch("requests.Session.request", side_effect=requests.Timeout):
        with pytest.raises(ProviderError, match="unavailable"):
            request_json("Test", "https://example.invalid")
    with patch("requests.Session.request") as request:
        request.return_value.status_code = 429
        with pytest.raises(ProviderError, match="quota"):
            request_json("Test", "https://example.invalid")


def test_units_rejected():
    import pytest

    with patch("trips.providers.request_json", return_value={"hourly_units": {"snowfall": "mm"}}):
        with pytest.raises(ProviderError, match="units"):
            forecast_batch([[0, 0]])


def test_cache_reuses_provider_result():
    with patch("requests.Session.request") as request:
        request.return_value.status_code = 200
        request.return_value.json.return_value = {"ok": True}
        assert request_json("Test", "https://example.invalid") == {"ok": True}
        assert request_json("Test", "https://example.invalid") == {"ok": True}
        assert request.call_count == 1
