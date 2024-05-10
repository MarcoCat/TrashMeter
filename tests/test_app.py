# tests/test_app.py
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture(scope='module')
def test_client():
    app = create_app()
    testing_client = app.test_client()

    # Establish an application context
    ctx = app.app_context()
    ctx.push()

    db.create_all()

    yield testing_client  # this is where the testing happens!

    db.session.remove()
    db.drop_all()
    ctx.pop()

def test_example(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    
def test_example2(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
