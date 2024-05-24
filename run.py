from app import create_app, db
from app.models import User, Organization, TrashCounter
from werkzeug.security import generate_password_hash
import os

def get_or_create(model, defaults=None, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        print(f"{model.__name__} with {kwargs} already exists.")
        return instance
    else:
        params = kwargs.copy()
        if defaults:
            params.update(defaults)
        instance = model(**params)
        db.session.add(instance)
        db.session.commit()
        print('b')
        return instance

def read_image(file_path):
    if not os.path.exists(file_path):
        print(f"Image file {file_path} not found.")
        return None
    with open(file_path, 'rb') as file:
        return file.read()

def create_test_data():
    ubc_image = read_image(os.path.join('app', 'static', 'uploads', 'ubc.jpg'))
    bcit_image = read_image(os.path.join('app', 'static', 'uploads', 'bcit.jpg'))
    langara_image = read_image(os.path.join('app', 'static', 'uploads', 'langara.jpg'))
    telus_image = read_image(os.path.join('app', 'static', 'uploads', 'telus.jpg'))
    rbc_image = read_image(os.path.join('app', 'static', 'uploads', 'rbc.jpg'))
    vancity_image = read_image(os.path.join('app', 'static', 'uploads', 'vancity.jpg'))
    red_cross_image = read_image(os.path.join('app', 'static', 'uploads', 'red_cross.jpg'))
    greenpeace_image = read_image(os.path.join('app', 'static', 'uploads', 'greenpeace.jpg'))
    habitat_humanity_image = read_image(os.path.join('app', 'static', 'uploads', 'habitat_humanity.jpg'))

    ubc = get_or_create(Organization, name='University of British Columbia', defaults={'type': 'school', 'address': '123 University Blvd', 'image': ubc_image})
    bcit = get_or_create(Organization, name='British Columbia Institute of Technology', defaults={'type': 'school', 'address': '456 Institute Rd', 'image': bcit_image})
    langara = get_or_create(Organization, name='Langara College', defaults={'type': 'school', 'address': '789 College St', 'image': langara_image})
    telus = get_or_create(Organization, name='Telus', defaults={'type': 'company', 'address': '101 Telus Ave', 'image': telus_image, 'total_trash': 100})
    rbc = get_or_create(Organization, name='RBC', defaults={'type': 'company', 'address': '202 RBC Blvd', 'image': rbc_image, 'total_trash': 150})
    vancity = get_or_create(Organization, name='Vancity', defaults={'type': 'company', 'address': '303 Vancity Rd', 'image': vancity_image, 'total_trash': 120})
    red_cross = get_or_create(Organization, name='Red Cross', defaults={'type': 'volunteer', 'address': '404 Volunteer Ln', 'image': red_cross_image, 'total_trash': 200})
    greenpeace = get_or_create(Organization, name='Greenpeace', defaults={'type': 'volunteer', 'address': '505 Environmental Rd', 'image': greenpeace_image, 'total_trash': 250})
    habitat_humanity = get_or_create(Organization, name='Habitat for Humanity', defaults={'type': 'volunteer', 'address': '606 Build St', 'image': habitat_humanity_image, 'total_trash': 180})

    users = [
        # Individual users
        {'username': 'john_doe', 'password': generate_password_hash('password123'), 'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.com', 'account_type': 'individual', 'trash_collected': 10, 'unallocated_trash': 5},
        {'username': 'alice_jones', 'password': generate_password_hash('password123'), 'first_name': 'Alice', 'last_name': 'Jones', 'email': 'alice.jones@example.com', 'account_type': 'individual', 'trash_collected': 20, 'unallocated_trash': 10},
        {'username': 'bob_brown', 'password': generate_password_hash('password123'), 'first_name': 'Bob', 'last_name': 'Brown', 'email': 'bob.brown@example.com', 'account_type': 'individual', 'trash_collected': 15, 'unallocated_trash': 5},

        # School users
        {'username': 'ubc_student', 'password': generate_password_hash('password123'), 'first_name': 'Emma', 'last_name': 'Smith', 'email': 'emma.smith@ubc.ca', 'account_type': 'school', 'organization_id': ubc.id, 'trash_collected': 30, 'unallocated_trash': 15},
        {'username': 'bcit_student', 'password': generate_password_hash('password123'), 'first_name': 'Liam', 'last_name': 'Johnson', 'email': 'liam.johnson@bcit.ca', 'account_type': 'school', 'organization_id': bcit.id, 'trash_collected': 25, 'unallocated_trash': 10},
        {'username': 'langara_teacher', 'password': generate_password_hash('password123'), 'first_name': 'Olivia', 'last_name': 'Williams', 'email': 'olivia.williams@langara.ca', 'account_type': 'school', 'organization_id': langara.id, 'trash_collected': 35, 'unallocated_trash': 20},

        # Company users
        {'username': 'telus_employee', 'password': generate_password_hash('password123'), 'first_name': 'James', 'last_name': 'Brown', 'email': 'james.brown@telus.com', 'account_type': 'company', 'organization_id': telus.id, 'trash_collected': 40, 'unallocated_trash': 20},
        {'username': 'rbc_employee', 'password': generate_password_hash('password123'), 'first_name': 'Sophia', 'last_name': 'Martinez', 'email': 'sophia.martinez@rbc.com', 'account_type': 'company', 'organization_id': rbc.id, 'trash_collected': 50, 'unallocated_trash': 25},
        {'username': 'vancity_employee', 'password': generate_password_hash('password123'), 'first_name': 'William', 'last_name': 'Garcia', 'email': 'william.garcia@vancity.com', 'account_type': 'company', 'organization_id': vancity.id, 'trash_collected': 45, 'unallocated_trash': 15},

        # Volunteer users
        {'username': 'red_cross_volunteer', 'password': generate_password_hash('password123'), 'first_name': 'Anna', 'last_name': 'Taylor', 'email': 'anna.taylor@redcross.org', 'account_type': 'volunteer', 'organization_id': red_cross.id, 'trash_collected': 60, 'unallocated_trash': 30},
        {'username': 'greenpeace_volunteer', 'password': generate_password_hash('password123'), 'first_name': 'Ethan', 'last_name': 'Clark', 'email': 'ethan.clark@greenpeace.org', 'account_type': 'volunteer', 'organization_id': greenpeace.id, 'trash_collected': 70, 'unallocated_trash': 35},
        {'username': 'habitat_humanity_volunteer', 'password': generate_password_hash('password123'), 'first_name': 'Sophia', 'last_name': 'White', 'email': 'sophia.white@habitat.org', 'account_type': 'volunteer', 'organization_id': habitat_humanity.id, 'trash_collected': 55, 'unallocated_trash': 25}
    ]

    for user_data in users:
        get_or_create(User, email=user_data['email'], defaults=user_data)

    print("Test users created successfully!")

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        create_test_data()
    app.run(debug=True)
