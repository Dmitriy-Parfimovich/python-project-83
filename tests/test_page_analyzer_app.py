import pytest
from page_analyzer.app import app


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
