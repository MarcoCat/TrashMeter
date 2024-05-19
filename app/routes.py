from flask import current_app as app
from flask import render_template, request, redirect, url_for, session, flash, g, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from . import db, mail
from .models import User, Organization
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import io
import os

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

@app.route('/')
def index():
    return render_template('home.html')

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
        position = request.form.get('position')
        organization_id = request.form.get('organization_id')
        
        if account_type in ['school', 'company', 'volunteer'] and not organization_id:
            flash(f'You must select an {account_type} for {account_type} accounts.', 'danger')
        else:
            new_user = User(username=username,
                            password=password,
                            first_name=first_name,
                            last_name=last_name,
                            account_type=account_type,
                            email=email,
                            position=position,
                            organization_id=organization_id)
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html', organizations=organizations)


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
    if g.user is not None:
        return render_template('profile.html', user=g.user)
    return 'User not found', 404

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(g.user.id)
    user.username = request.form['username']
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.email = request.form['email']
    user.account_type = request.form['account_type']
    user.position = request.form.get('position')

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

@app.route('/leaderboard')
def leaderboard():
    # Leaderboard for all users
    users = User.query.order_by(User.trash_collected.desc()).all()

    # Leaderboard for companies
    companies = db.session.query(
        Organization.name,
        Organization.total_trash
    ).filter(Organization.type == 'company').order_by(db.desc(Organization.total_trash)).all()

    # Leaderboard for schools
    schools = db.session.query(
        Organization.name,
        Organization.total_trash
    ).filter(Organization.type == 'school').order_by(db.desc(Organization.total_trash)).all()

    # Leaderboard for volunteer organizations
    volunteers = db.session.query(
        Organization.name,
        Organization.total_trash
    ).filter(Organization.type == 'volunteer').order_by(db.desc(Organization.total_trash)).all()

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

        new_org = Organization(
            name=request.form['organization_name'],
            type=org_type,
            address=request.form['organization_address'],
            image=image_data
        )
        db.session.add(new_org)
        db.session.commit()
        return redirect(url_for('search', type=org_type))

    org_type = request.args.get('type', 'organization')
    return render_template('create_information.html', account_type=org_type)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('searchQuery', '')
    org_type = request.args.get('type', '')

    if org_type not in ['school', 'company', 'volunteer']:
        org_type = ''

    if query:
        results = Organization.query.filter(
            Organization.name.ilike(f"%{query}%"),
            Organization.type.ilike(f"%{org_type}%")
        ).all()
    else:
        results = []

    return render_template('search.html', results=results, query=query, org_type=org_type)

