from app import create_app, db
from app.models import User, Organization
from werkzeug.security import generate_password_hash

def get_or_create(model, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

def create_test_users():
    # Create or get existing organizations
    ubc = get_or_create(Organization, name='University of British Columbia', type='school')
    bcit = get_or_create(Organization, name='British Columbia Institute of Technology', type='school')
    langara = get_or_create(Organization, name='Langara College', type='school')
    telus = get_or_create(Organization, name='Telus', type='company')
    rbc = get_or_create(Organization, name='RBC', type='company')
    vancity = get_or_create(Organization, name='Vancity', type='company')

    users = [
        # Individual users
        User(username='john_doe', password=generate_password_hash('password123'), first_name='John', last_name='Doe', email='john.doe@example.com', account_type='individual', trash_collected=10),
        User(username='alice_jones', password=generate_password_hash('password123'), first_name='Alice', last_name='Jones', email='alice.jones@example.com', account_type='individual', trash_collected=20),
        User(username='bob_brown', password=generate_password_hash('password123'), first_name='Bob', last_name='Brown', email='bob.brown@example.com', account_type='individual', trash_collected=15),
        
        # School users
        User(username='ubc_student', password=generate_password_hash('password123'), first_name='Emma', last_name='Smith', email='emma.smith@ubc.ca', account_type='school', position='student', organization_id=ubc.id, trash_collected=30),
        User(username='bcit_student', password=generate_password_hash('password123'), first_name='Liam', last_name='Johnson', email='liam.johnson@bcit.ca', account_type='school', position='student', organization_id=bcit.id, trash_collected=25),
        User(username='langara_teacher', password=generate_password_hash('password123'), first_name='Olivia', last_name='Williams', email='olivia.williams@langara.ca', account_type='school', position='teacher', organization_id=langara.id, trash_collected=35),
        User(username='bcit_student2', password=generate_password_hash('password123'), first_name='John', last_name='Chang', email='john.chang@bcit.ca', account_type='school', position='student', organization_id=bcit.id, trash_collected=20),
        
        # Company users
        User(username='telus_employee', password=generate_password_hash('password123'), first_name='James', last_name='Brown', email='james.brown@telus.com', account_type='company', position='employee', organization_id=telus.id, trash_collected=40),
        User(username='rbc_employee', password=generate_password_hash('password123'), first_name='Sophia', last_name='Martinez', email='sophia.martinez@rbc.com', account_type='company', position='employee', organization_id=rbc.id, trash_collected=50),
        User(username='vancity_employee', password=generate_password_hash('password123'), first_name='William', last_name='Garcia', email='william.garcia@vancity.com', account_type='company', position='employee', organization_id=vancity.id, trash_collected=45)
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
    with app.app_context():
        create_test_users()
    app.run(debug=True)
