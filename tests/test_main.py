from fastapi.testclient import TestClient
from app.main import app

# Create a test client for our app
client = TestClient(app)


def test_read_root():
    # Make a simulated GET request to the "/" endpoint
    response = client.get("/")
    
    # Check if the response status code is 200 (OK)
    assert response.status_code == 200
    
    # Check if the response body is the correct JSON
    assert response.json() == {"status": "API is running"}