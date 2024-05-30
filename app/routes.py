import smtplib
from flask import current_app as app
from flask import render_template, request, redirect, url_for, session, flash, g, send_file
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from . import db, mail
from .models import User, Organization, TempUser, TrashCounter, TrashHistory
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import io
import os
from rapidfuzz import fuzz
from sqlalchemy.exc import IntegrityError
import random
import string
from validate_email_address import validate_email


# Utility function to check if a user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to view this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Load user before request if user is logged in
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)

# Utility function to get or create a model instance
def get_or_create(model, defaults=None, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = kwargs.copy()
        if defaults:
            params.update(defaults)
        instance = model(**params)
        db.session.add(instance)
        try:
            db.session.commit()
            return instance, True
        except IntegrityError:
            db.session.rollback()
            return None, False

# Utility function to update a model instance with unique constraint checks
def update_instance(instance, **kwargs):
    for key, value in kwargs.items():
        setattr(instance, key, value)
    try:
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        flash(f"An instance with the given attributes already exists.", "danger")
        return False

def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def index():
    db.session.add(TrashCounter(total_trash_collected=0))  # Initial value
    db.session.commit()
    return render_template('home.html')


@app.route('/trash_meter')
def trash_meter():
    if 'user_id' not in session:
        return redirect(url_for('landing'))
    # db.session.add(TrashCounter(total_trash_collected=0))  # Initial value
    # db.session.commit()
    user = db.session.get(User, g.user.id)
    total_trash = TrashCounter.query.first()
    history = user.trash_history
    return render_template('trash_meter.html',
                            user=user, total_trash=total_trash.total_trash_collected, history=history)

@app.route('/landing')
def landing():
    # db.session.add(TrashCounter(total_trash_collected=0))  # Initial value
    # db.session.commit()
    total_trash = TrashCounter.query.first()
    return render_template('trash_meter_landing.html', total_trash=total_trash.total_trash_collected)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect logged in users
    if 'user_id' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('You were successfully logged in.', 'info')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        flash('You are already logged in. No need to sign up again.', 'info')
        return redirect(url_for('index'))

    organizations = Organization.query.all()

    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        account_type = request.form['account_type']
        email = request.form['email']
        organization_name = request.form.get('organization_name')

        if not validate_email(email):
            flash('Invalid email address.', 'danger')
            return render_template('signup.html', organizations=organizations)

        organization = Organization.query.filter_by(name=organization_name).first()
        organization_id = organization.id if organization else None
        organization_type = organization.type if organization else None

        if account_type in ['school', 'company', 'volunteer'] and not organization_id:
            flash(f'You must select an {account_type} for {account_type} accounts.', 'danger')
        elif account_type in ['school', 'company', 'volunteer'] and organization_type != account_type:
            flash(f'The selected organization type does not match the account type: {account_type}.', 'danger')
        else:
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                flash('A user with the given username or email already exists.', 'danger')
                return render_template('signup.html', organizations=organizations)

            existing_temp_user = TempUser.query.filter((TempUser.username == username) | (TempUser.email == email)).first()
            if existing_temp_user:
                flash('A signup request with the given username or email already exists. Please check your email for the verification code.', 'danger')
                return render_template('signup.html', organizations=organizations)

            verification_code = generate_verification_code()
            temp_user, created = get_or_create(TempUser, username=username, defaults={
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'account_type': account_type,
                'email': email,
                'organization_id': organization_id,
                'verification_code': verification_code
            })
            if not created:
                flash('A user with the given username or email already exists.', 'danger')
                return render_template('signup.html', organizations=organizations)

            msg = Message('Email Verification',
                          sender=app.config['MAIL_DEFAULT_SENDER'],
                          recipients=[email])
            msg.body = f'Your verification code is: {verification_code}'
            try:
                mail.send(msg)
                flash('Signup successful! Please check your email for a verification code.', 'success')
                return redirect(url_for('verify_email'))
            except smtplib.SMTPRecipientsRefused:
                db.session.delete(temp_user)
                db.session.commit()
                flash('Invalid email address. Please try again.', 'danger')

    return render_template('signup.html', organizations=organizations)

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'POST':
        email = request.form['email']
        verification_code = request.form['verification_code']
        temp_user = TempUser.query.filter_by(email=email, verification_code=verification_code).first()
        if temp_user:
            new_user = User(username=temp_user.username,
                            password=temp_user.password,
                            first_name=temp_user.first_name,
                            last_name=temp_user.last_name,
                            account_type=temp_user.account_type,
                            email=temp_user.email,
                            organization_id=temp_user.organization_id)
            db.session.add(new_user)
            db.session.delete(temp_user)
            db.session.commit()
            flash('Email verified! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid email or verification code.', 'danger')
    return render_template('verify_email.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])
            msg = Message('Password Reset Request', 
                          sender=app.config['MAIL_DEFAULT_SENDER'], 
                          recipients=[email])
            link = url_for('reset_password', token=token, _external=True)
            msg.body = f'Please click on the link to reset your password: {link}'
            mail.send(msg)
            return 'Please check your email for a password reset link.'
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)  # Token expires after 1 hour
    except SignatureExpired:
        flash('The password reset link is expired.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('reset_password', token=token))
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        user = User.query.get(g.user.id)
        if user and check_password_hash(user.password, old_password):
            if new_password == confirm_password:
                user.password = generate_password_hash(new_password)
                db.session.commit()
                flash('Your password has been updated.', 'success')
                return redirect(url_for('profile'))
            else:
                flash('New passwords do not match.', 'danger')
        else:
            flash('Incorrect old password.', 'danger')
    return render_template('change_password.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=g.user)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = db.session.get(User, g.user.id)
    updated = update_instance(user,
                              username=request.form['username'],
                              first_name=request.form['first_name'],
                              last_name=request.form['last_name'],
                              email=request.form['email'])

    if not updated:
        return redirect(url_for('profile'))

    profile_picture = request.files.get('profile_image')
    if profile_picture:
        user.profile_picture = profile_picture.read()

    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/profile_picture/<int:user_id>')
def profile_picture(user_id):
    user = User.query.get(user_id)
    if user and user.profile_picture:
        return send_file(
            io.BytesIO(user.profile_picture),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name='profile_picture.jpg'
        )
    else:
        # Return the default profile picture if no user or profile picture is found
        default_image_path = os.path.join(app.root_path, 'static/images/user_icon.png')
        return send_file(default_image_path, mimetype='image/jpeg')

@app.route('/update_trash', methods=['POST'])
@login_required
def update_trash():
    if request.method == 'POST':
        trash_amount = int(request.form['trash_amount'])
        user = db.session.get(User, g.user.id)
        user.trash_collected += trash_amount
        user.unallocated_trash += trash_amount
        db.session.commit()
        flash('Trash collection updated successfully!', 'success')
        return redirect(url_for('profile'))


@app.route('/update', methods=['POST'])
def update_trash_counter():
    user = db.session.get(User, g.user.id)
    total_trash = TrashCounter.query.first()
    session['total_trash'] = total_trash.total_trash_collected
    amount = int(request.form['picked_up'])
    beach = request.form['beach']

    trash_history = TrashHistory(
        picked_up=amount,
        beach=beach,
        user_id=user.id
    )
    db.session.add(trash_history)

    user.trash_collected += amount
    user.unallocated_trash += amount
    total_trash.total_trash_collected += amount
    user.beach = beach
    db.session.commit()

    return redirect(url_for('trash_meter'))

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.trash_collected.desc()).all()
    companies = Organization.query.filter_by(type='company').order_by(Organization.total_trash.desc()).all()
    schools = Organization.query.filter_by(type='school').order_by(Organization.total_trash.desc()).all()
    volunteers = Organization.query.filter_by(type='volunteer').order_by(Organization.total_trash.desc()).all()

    return render_template('leaderboard.html', users=users, companies=companies, schools=schools, volunteers=volunteers)

@app.route('/allocate_trash', methods=['GET', 'POST'])
@login_required
def allocate_trash():
    if request.method == 'POST':
        organization_id = int(request.form['organization_id'])
        trash_amount = int(request.form['trash_amount'])
        user = db.session.get(User, g.user.id)

        if trash_amount > user.unallocated_trash:
            flash('You cannot allocate more trash than you have unallocated.', 'danger')
            return redirect(url_for('allocate_trash'))

        user.unallocated_trash -= trash_amount

        # Update organization score
        organization = db.session.get(Organization, organization_id)
        if organization:
            organization.total_trash = (organization.total_trash or 0) + trash_amount
            db.session.commit()
            flash(f'{trash_amount} pieces of trash allocated to {organization.name} successfully!', 'success')
        else:
            flash('Organization not found.', 'danger')

        return redirect(url_for('profile'))

    organizations = Organization.query.all()
    return render_template('allocate_trash.html', organizations=organizations)

@app.route('/createinformation', methods=['GET', 'POST'])
def create_information():

    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if request.method == 'POST':
        # Handle image upload
        image_file = request.files.get('organization_image')
        image_data = None
        if image_file and allowed_file(image_file.filename):
            image_data = image_file.read()

        org_type = request.form['organization_type']
        if org_type not in ['school', 'company', 'volunteer']:
            flash("Invalid organization type.")
            return redirect(request.url)

        new_org, created = get_or_create(Organization, name=request.form['organization_name'], defaults={
            'type': org_type,
            'address': request.form['organization_address'],
            'image': image_data
        })
        if created:
            flash('Organization created successfully!', 'success')
            return redirect(url_for('search', type=org_type))
        else:
            flash('An organization with the given attributes already exists.', 'danger')

    org_type = request.args.get('type', 'organization')
    return render_template('create_information.html', account_type=org_type)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('searchQuery', '')
    org_type = request.args.get('type', '')

    if org_type not in ['school', 'company', 'volunteer']:
        org_type = ''

    results = []
    if query:
        organizations = Organization.query.all()
        for org in organizations:
            if org_type and org.type.lower() != org_type.lower():
                continue
            if fuzz.partial_ratio(query.lower(), org.name.lower()) > 85:
                results.append(org)

    return render_template('search.html', results=results, query=query, org_type=org_type)

@app.route('/organization_image/<int:organization_id>')
def organization_image(organization_id):
    organization = Organization.query.get_or_404(organization_id)
    if organization.image:
        return send_file(
            io.BytesIO(organization.image),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=f'{organization.name}.jpg'
        )
    else:
        return redirect(url_for('static', filename='images/user_icon.png'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
