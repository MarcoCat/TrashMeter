import pytest
import io
from flask import url_for
from app import create_app, db
from app.models import User, Organization, TempUser
from werkzeug.security import generate_password_hash
from unittest.mock import patch

@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing purposes

    with app.app_context():
        db.create_all()

        # Create initial data
        org1 = Organization(name='Org1', type='company', address='123 Company St', total_trash=0)
        org2 = Organization(name='Org2', type='company', address='456 Company Rd', total_trash=0)
        db.session.add_all([org1, org2])
        
        test_user = User(username='testuser',
                         password=generate_password_hash('password123'),
                         first_name='Test',
                         last_name='User',
                         email='test@example.com',
                         account_type='school')
        db.session.add(test_user)
        db.session.commit()

        yield app

        db.drop_all()
        db.session.remove()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    with app.app_context():
        # Ensure the database is clean before each test
        db.session.query(User).delete()
        db.session.query(Organization).delete()
        db.session.commit()

        # Create initial data for each test
        org1 = Organization(name='Org1', type='company', address='123 Company St', total_trash=0)
        org2 = Organization(name='Org2', type='company', address='456 Company Rd', total_trash=0)
        db.session.add_all([org1, org2])
        
        test_user = User(username='testuser',
                         password=generate_password_hash('password123'),
                         first_name='Test',
                         last_name='User',
                         email='test@example.com',
                         account_type='school')
        db.session.add(test_user)
        db.session.commit()

        yield db

def login_test_user(client):
    return client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)

def test_example(client, init_database):
    response = client.get('/')
    assert response.status_code == 200

def test_signup(client, init_database):
    with client.application.app_context():
        organization = Organization(name='School1', type='school', address='789 School Ln', total_trash=0)
        db.session.add(organization)
        db.session.commit()
        organization_id = organization.id

    with patch('flask_mail.Mail.send') as mock_mail_send:
        response = client.post('/signup', data={
            'username': 'newuser',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User',
            'account_type': 'school',
            'email': 'newuser@example.com',
            'organization_name': 'School1'
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_mail_send.assert_called_once()

        # Ensure TempUser is created
        with client.application.app_context():
            temp_user = TempUser.query.filter_by(username='newuser').first()
            assert temp_user is not None
            assert temp_user.email == 'newuser@example.com'
            assert temp_user.organization_id == organization_id

        # Simulate email verification
        verification_code = temp_user.verification_code
        response = client.post('/verify_email', data={
            'email': 'newuser@example.com',
            'verification_code': verification_code
        }, follow_redirects=True)
        assert response.status_code == 200

    # Check if User is created after verification
    with client.application.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert user.organization_id == organization_id

def test_update_trash(client, init_database):
    login_test_user(client)
    response = client.post('/update_trash', data={'trash_amount': 5}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Trash collection updated successfully!' in response.data

def test_allocate_trash(client, init_database):
    login_test_user(client)
    
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        org1 = Organization.query.filter_by(name='Org1').first()
        user.unallocated_trash = 10
        db.session.commit()

        response = client.post('/allocate_trash', data={'organization_id': org1.id, 'trash_amount': 5}, follow_redirects=True)
        assert response.status_code == 200

        # Verify the database state
        user = User.query.filter_by(username='testuser').first()
        assert user.unallocated_trash == 5

        organization = Organization.query.filter_by(id=org1.id).first()
        assert organization.total_trash == 5

def test_profile_update(client, init_database):
    login_test_user(client)
    response = client.post('/update_profile', data={
        'username': 'updateduser',
        'first_name': 'Updated',
        'last_name': 'User',
        'email': 'updated@example.com',
        'account_type': 'school'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Profile updated successfully!' in response.data

def test_image_upload(client, init_database):
    login_test_user(client)
    data = {
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'account_type': 'school',
        'profile_image': (io.BytesIO(b"fake image data"), 'test.jpg')
    }
    response = client.post('/update_profile', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'Profile updated successfully!' in response.data

def test_create_test_users(client, init_database):
    with client.application.app_context():
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
    org1 = get_or_create(Organization, name='Org1', type='company', address='123 Company St')
    org2 = get_or_create(Organization, name='Org2', type='company', address='456 Company Rd')

    users = [
        User(username='user1', password=generate_password_hash('password123'), first_name='User', last_name='One', email='user1@example.com', account_type='school'),
        User(username='user2', password=generate_password_hash('password123'), first_name='User', last_name='Two', email='user2@example.com', account_type='school')
    ]

    for user in users:
        db.session.add(user)
    db.session.commit()

def test_leaderboard(client, init_database):
    login_test_user(client)
    response = client.get('/leaderboard')
    assert response.status_code == 200
    assert b'Leaderboard' in response.data

def test_logout(client, init_database):
    login_test_user(client)
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out.' in response.data
