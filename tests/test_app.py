import pytest
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost.localdomain'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

        # Create a test user
        test_user = User(username='testuser',
                         password=generate_password_hash('password123'),
                         first_name='Test',
                         last_name='User',
                         email='test@example.com',
                         account_type='regular',
                         position='user')
        db.session.add(test_user)
        db.session.commit()

    yield app.test_client()

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def login_test_user(test_client):
    """Log in the test user."""
    response = test_client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    return response

def test_example(test_client):
    response = test_client.get('/')
    assert response.status_code == 200

def test_update_trash(test_client, login_test_user):
    """Test updating trash collected."""
    response = test_client.post('/update_trash', data={
        'trash_amount': 5
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Trash collection updated successfully!' in response.data

    # Verify the user's trash_collected value is updated
    with test_client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user.trash_collected == 5
