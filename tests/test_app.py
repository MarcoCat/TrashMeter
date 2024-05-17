import pytest
import io
from app import create_app, db
from app.models import User, Organization
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost.localdomain'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

        org1 = Organization(name='Org1', type='company', total_trash=0)
        org2 = Organization(name='Org2', type='company', total_trash=0)
        db.session.add_all([org1, org2])
        
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

def test_allocate_trash(test_client, login_test_user):
    """Test allocating trash to an organization."""
    with test_client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        user.unallocated_trash = 10
        db.session.commit()

    response = test_client.post('/allocate_trash', data={
        'organization_id': 1,
        'trash_amount': 5
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'5 pieces of trash allocated to Org1 successfully!' in response.data

    with test_client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        org = Organization.query.filter_by(id=1).first()
        assert user.unallocated_trash == 5
        assert org.total_trash == 5

def test_profile_update(test_client, login_test_user):
    """Test updating user profile."""
    response = test_client.post('/update_profile', data={
        'username': 'updateduser',
        'first_name': 'Updated',
        'last_name': 'User',
        'email': 'updated@example.com',
        'account_type': 'regular',
        'position': 'user'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Profile updated successfully!' in response.data

    # Verify the user's profile is updated
    with test_client.application.app_context():
        user = User.query.filter_by(username='updateduser').first()
        assert user is not None
        assert user.first_name == 'Updated'
        assert user.email == 'updated@example.com'

def test_image_upload(test_client, login_test_user):
    """Test uploading and saving profile image."""
    data = {
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'account_type': 'regular',
        'position': 'user',
        'profile_image': (io.BytesIO(b"fake image data"), 'test.jpg')
    }

    response = test_client.post('/update_profile', data=data, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b'Profile updated successfully!' in response.data

    with test_client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user.profile_picture is not None

def test_create_test_users(test_client):
    """Test creating test users."""
    with test_client.application.app_context():
        users = User.query.all()
        assert len(users) == 1

        create_test_users()

        users = User.query.all()
        assert len(users) > 1

def get_or_create(model, defaults=None, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        params = kwargs.copy()
        if defaults:
            params.update(defaults)
        instance = model(**params)
        db.session.add(instance)
        db.session.commit()
        return instance

def create_test_users():
    org1 = get_or_create(Organization, name='Org1', type='company')
    org2 = get_or_create(Organization, name='Org2', type='company')

    users = [
        User(username='user1', password=generate_password_hash('password123'), first_name='User', last_name='One', email='user1@example.com', account_type='regular', position='user'),
        User(username='user2', password=generate_password_hash('password123'), first_name='User', last_name='Two', email='user2@example.com', account_type='regular', position='user')
    ]

    for user in users:
        db.session.add(user)
    db.session.commit()
