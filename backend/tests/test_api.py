from .conftest import register
from datetime import datetime, timezone
from app.sync_celestrak import parse_tle_catalog, propagate


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_registration_login_and_invalid_credentials(client):
    response = register(client)
    assert response.json()["email"] == "pilot@example.com"
    assert "password" not in response.text
    assert response.headers["X-CSRF-Token"] == client.cookies.get("smc_csrf")
    refreshed = client.get("/api/v1/auth/me")
    assert refreshed.headers["X-CSRF-Token"] == client.cookies.get("smc_csrf")
    client.cookies.clear()
    assert client.post("/api/v1/auth/login", json={"email": "pilot@example.com", "password": "wrong"}).status_code == 401
    assert client.post("/api/v1/auth/login", json={"email": "pilot@example.com", "password": "strong-password-123"}).status_code == 200


def test_protected_route_and_satellite_catalog(client):
    assert client.get("/api/v1/watchlist").status_code == 401
    response = client.get("/api/v1/satellites?orbit=LEO&search=ISS")
    assert response.status_code == 200
    assert response.json()["items"][0]["norad_id"] == 25544
    assert response.json()["items"][0]["data_quality"] == "demo_propagated_estimate"


def test_watchlist_crud(auth_client):
    created = auth_client.post("/api/v1/watchlist", json={"satellite_id": 1, "notes": "Evening pass", "notify": True})
    assert created.status_code == 201
    item_id = created.json()["id"]
    assert len(auth_client.get("/api/v1/watchlist").json()) == 1
    updated = auth_client.patch(f"/api/v1/watchlist/{item_id}", json={"notes": "Updated"})
    assert updated.json()["notes"] == "Updated"
    assert auth_client.delete(f"/api/v1/watchlist/{item_id}").status_code == 204


def test_mission_crud(auth_client):
    created = auth_client.post("/api/v1/missions", json={"name": "Aurora Survey", "description": "Polar imaging",
                                                           "status": "active", "priority": "high", "satellite_ids": [3, 4]})
    assert created.status_code == 201
    mission_id = created.json()["id"]
    updated = auth_client.patch(f"/api/v1/missions/{mission_id}", json={"status": "completed", "satellite_ids": [3]})
    assert updated.json()["status"] == "completed"
    assert len(updated.json()["satellites"]) == 1
    assert auth_client.delete(f"/api/v1/missions/{mission_id}").status_code == 204


def test_cross_user_isolation(client):
    register(client, "alpha@example.com")
    client.headers["X-CSRF-Token"] = client.cookies.get("smc_csrf")
    mission = client.post("/api/v1/missions", json={"name": "Private Mission", "satellite_ids": [1]}).json()
    client.cookies.clear(); client.headers.pop("X-CSRF-Token", None)
    register(client, "bravo@example.com")
    client.headers["X-CSRF-Token"] = client.cookies.get("smc_csrf")
    assert client.patch(f"/api/v1/missions/{mission['id']}", json={"name": "Intrusion"}).status_code == 404
    assert client.delete(f"/api/v1/missions/{mission['id']}").status_code == 404


def test_validation_and_csrf(auth_client):
    assert auth_client.post("/api/v1/missions", json={"name": "x"}).status_code == 422
    auth_client.headers["X-CSRF-Token"] = "invalid"
    assert auth_client.post("/api/v1/watchlist", json={"satellite_id": 1}).status_code == 403


def test_csrf_header_is_exposed_to_allowed_frontend_origin(client):
    response = client.post(
        "/api/v1/auth/register",
        headers={"Origin": "http://localhost:5173"},
        json={
            "email": "cors@example.com",
            "display_name": "CORS Pilot",
            "password": "strong-password-123",
        },
    )
    assert response.status_code == 201
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "X-CSRF-Token" in response.headers["access-control-expose-headers"]


def test_tle_parser_and_sgp4_propagation():
    line1 = "1 25544U 98067A   24001.50000000  .00016717  00000+0  30115-3 0  9998"
    line2 = "2 25544  51.6416  20.1234 0004735  82.2354  30.1234 15.50000000432109"
    records = parse_tle_catalog(f"ISS (ZARYA)\n{line1}\n{line2}\n")
    assert records == [("ISS (ZARYA)", line1, line2)]
    latitude, longitude, altitude, speed, period, inclination = propagate(line1, line2, datetime(2024, 1, 1, 12, tzinfo=timezone.utc))
    assert -90 <= latitude <= 90 and -180 <= longitude <= 180
    assert 300 < altitude < 500 and 7 < speed < 8
    assert 80 < period < 110 and 50 < inclination < 53
