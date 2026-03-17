import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

# 1. Health Check Test
def test_health_check():
    """Verify the service is alive"""
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

# 2. Test for 'aradhna6dec' (Mocked)
@patch("app.services.github.httpx.AsyncClient.get")
def test_get_aradhna_gists(mock_get):
    """
    Test retrieving gists for user 'aradhna6dec'.
    Note: We MOCK (fake) the response so tests pass even without internet.
    """
    # Mock Data (Jo GitHub se aana chahiye)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [{
        "id": "gist_aradhna_1",
        "url": "http://api.github.com/gists/1",
        "html_url": "http://gist.github.com/aradhna6dec/1",
        "created_at": "2024-02-13T00:00:00Z",
        "files": {
            "test.txt": {
                "size": 50,
                "raw_url": "http://raw.url/test.txt",
                "type": "text/plain"
            }
        }
    }]
    mock_get.return_value = mock_resp

    # Actual API Call to YOUR user
    response = client.get("/aradhna6dec")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "gist_aradhna_1"
    # Verify file content structure
    assert "test.txt" in data[0]["files"]

# 3. Error Handling Test
@patch("app.services.github.httpx.AsyncClient.get")
def test_user_not_found(mock_get):
    """Verify 404 handling"""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp

    response = client.get("/nonexistentuser12345")
    assert response.status_code == 404