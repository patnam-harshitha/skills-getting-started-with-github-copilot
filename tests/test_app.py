import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original_activities


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_for_activity():
    # Arrange
    url = "/activities/Chess Club/signup"
    email = "test.student@mergington.edu"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}


def test_signup_for_missing_activity_returns_404():
    # Arrange
    url = "/activities/Nonexistent/signup"
    email = "x@y.com"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity():
    # Arrange
    signup_url = "/activities/Chess Club/signup"
    unregister_url = "/activities/Chess Club/unregister"
    email = "unregister.student@mergington.edu"
    client.post(signup_url, params={"email": email})

    # Act
    response = client.post(unregister_url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}


def test_unregister_not_registered_returns_400():
    # Arrange
    url = "/activities/Chess Club/unregister"
    email = "missing@mergington.edu"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"
