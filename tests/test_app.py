
import httpx

BASE_URL = "http://127.0.0.1:8000"


def test_health_check():
    response = httpx.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_dashboard():
    response = httpx.get(f"{BASE_URL}/")
    assert response.status_code == 200


def test_candidates_api():
    response = httpx.get(f"{BASE_URL}/api/candidates")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_invalid_status():
    response = httpx.post(
        f"{BASE_URL}/candidates/1/status",
        data={"status": "InvalidStatus"}
    )
    assert response.status_code == 400
