from src.app import app
import pytest

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_root(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'ok'
