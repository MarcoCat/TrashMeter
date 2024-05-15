from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def create_test_users():
    users = [
        # Individual users
        User(username='john_doe', password=generate_password_hash('password123'), first_name='John', last_name='Doe', email='john.doe@example.com', account_type='individual'),
        User(username='alice_jones', password=generate_password_hash('password123'), first_name='Alice', last_name='Jones', email='alice.jones@example.com', account_type='individual'),
        User(username='bob_brown', password=generate_password_hash('password123'), first_name='Bob', last_name='Brown', email='bob.brown@example.com', account_type='individual'),
        
        # School users
        User(username='ubc_student', password=generate_password_hash('password123'), first_name='Emma', last_name='Smith', email='emma.smith@ubc.ca', account_type='school', position='student'),
        User(username='bcit_student', password=generate_password_hash('password123'), first_name='Liam', last_name='Johnson', email='liam.johnson@bcit.ca', account_type='school', position='student'),
        User(username='langara_student', password=generate_password_hash('password123'), first_name='Olivia', last_name='Williams', email='olivia.williams@langara.ca', account_type='school', position='teacher'),
        
        # Company users
        User(username='telus_employee', password=generate_password_hash('password123'), first_name='James', last_name='Brown', email='james.brown@telus.com', account_type='company', position='employee'),
        User(username='rbc_employee', password=generate_password_hash('password123'), first_name='Sophia', last_name='Martinez', email='sophia.martinez@rbc.com', account_type='company', position='employee'),
        User(username='vancity_employee', password=generate_password_hash('password123'), first_name='William', last_name='Garcia', email='william.garcia@vancity.com', account_type='company', position='employee')
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
