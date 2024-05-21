from app import create_app, db
from app.models import User, Organization
from werkzeug.security import generate_password_hash

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
    ubc = get_or_create(Organization, name='University of British Columbia', type='school', address='123 University Blvd', image=None)
    bcit = get_or_create(Organization, name='British Columbia Institute of Technology', type='school', address='456 Institute Rd', image=None)
    langara = get_or_create(Organization, name='Langara College', type='school', address='789 College St', image=None)
    telus = get_or_create(Organization, name='Telus', type='company', defaults={'address': '101 Telus Ave', 'image': None, 'total_trash': 100})
    rbc = get_or_create(Organization, name='RBC', type='company', defaults={'address': '202 RBC Blvd', 'image': None, 'total_trash': 150})
    vancity = get_or_create(Organization, name='Vancity', type='company', defaults={'address': '303 Vancity Rd', 'image': None, 'total_trash': 120})

    # Adding volunteer organizations
    red_cross = get_or_create(Organization, name='Red Cross', type='volunteer', address='404 Volunteer Ln', image=None, defaults={'total_trash': 200})
    greenpeace = get_or_create(Organization, name='Greenpeace', type='volunteer', address='505 Environmental Rd', image=None, defaults={'total_trash': 250})
    habitat_humanity = get_or_create(Organization, name='Habitat for Humanity', type='volunteer', address='606 Build St', image=None, defaults={'total_trash': 180})

    users = [
        # Individual users
        User(username='john_doe', password=generate_password_hash('password123'), first_name='John', last_name='Doe', email='john.doe@example.com', account_type='individual', trash_collected=10, unallocated_trash=5),
        User(username='alice_jones', password=generate_password_hash('password123'), first_name='Alice', last_name='Jones', email='alice.jones@example.com', account_type='individual', trash_collected=20, unallocated_trash=10),
        User(username='bob_brown', password=generate_password_hash('password123'), first_name='Bob', last_name='Brown', email='bob.brown@example.com', account_type='individual', trash_collected=15, unallocated_trash=5),
        
        # School users
        User(username='ubc_student', password=generate_password_hash('password123'), first_name='Emma', last_name='Smith', email='emma.smith@ubc.ca', account_type='school', position='student', organization_id=ubc.id, trash_collected=30, unallocated_trash=15),
        User(username='bcit_student', password=generate_password_hash('password123'), first_name='Liam', last_name='Johnson', email='liam.johnson@bcit.ca', account_type='school', position='student', organization_id=bcit.id, trash_collected=25, unallocated_trash=10),
        User(username='langara_teacher', password=generate_password_hash('password123'), first_name='Olivia', last_name='Williams', email='olivia.williams@langara.ca', account_type='school', position='teacher', organization_id=langara.id, trash_collected=35, unallocated_trash=20),
        
        # Company users
        User(username='telus_employee', password=generate_password_hash('password123'), first_name='James', last_name='Brown', email='james.brown@telus.com', account_type='company', position='employee', organization_id=telus.id, trash_collected=40, unallocated_trash=20),
        User(username='rbc_employee', password=generate_password_hash('password123'), first_name='Sophia', last_name='Martinez', email='sophia.martinez@rbc.com', account_type='company', position='employee', organization_id=rbc.id, trash_collected=50, unallocated_trash=25),
        User(username='vancity_employee', password=generate_password_hash('password123'), first_name='William', last_name='Garcia', email='william.garcia@vancity.com', account_type='company', position='employee', organization_id=vancity.id, trash_collected=45, unallocated_trash=15),

        # Volunteer users
        User(username='red_cross_volunteer', password=generate_password_hash('password123'), first_name='Anna', last_name='Taylor', email='anna.taylor@redcross.org', account_type='volunteer', position='volunteer', organization_id=red_cross.id, trash_collected=60, unallocated_trash=30),
        User(username='greenpeace_volunteer', password=generate_password_hash('password123'), first_name='Ethan', last_name='Clark', email='ethan.clark@greenpeace.org', account_type='volunteer', position='volunteer', organization_id=greenpeace.id, trash_collected=70, unallocated_trash=35),
        User(username='habitat_humanity_volunteer', password=generate_password_hash('password123'), first_name='Sophia', last_name='White', email='sophia.white@habitat.org', account_type='volunteer', position='volunteer', organization_id=habitat_humanity.id, trash_collected=55, unallocated_trash=25)
    ]

    for user in users:
        # Check if the user already exists
        existing_user = User.query.filter_by(email=user.email).first()
        if existing_user:
            print(f"User with email {user.email} already exists.")
            continue
        
        # Add test users to the session
        db.session.add(user)
    
    # Commit the session to the database
    db.session.commit()
    print("Test users created successfully!")

app = create_app()

if __name__ == '__main__':
    # with app.app_context():
    #     create_test_users()
    app.run(debug=True)
