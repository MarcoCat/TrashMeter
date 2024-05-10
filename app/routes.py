from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app import app, db, mail
from app.models import User
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from sqlalchemy import desc



# Utility function to check if a user is logged in


trash_counter = 60000
personal_counter = 0
this_beach = ""
this_date = ""
this_picked = 0
trash_history = []
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
        g.user = User.query.get(user_id)

@app.route('/')
def index():
    if 'user_id' not in session:
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('login'))
    # trash_data = TrashData.query.first()
    return render_template('home.html', trash_counter=trash_counter, personal_counter=personal_counter,
                           trash_history=trash_history)
                           # , this_date=this_date, beach=this_beach, this_picked=this_picked)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    # Redirect logged in users
    if 'user_id' in session:
        flash('You are already logged in. No need to sign up again.', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        global trash_counter, personal_counter
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        account_type = request.form['account_type']
        email = request.form['email']
        position = request.form['position']
        new_user = User(username=username,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        account_type=account_type,
                        email=email,
                        position=position)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')


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

@app.route('/profile')
@login_required
def profile():
    if g.user is not None:
        return render_template('profile.html', user=g.user)
    return 'User not found', 404

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        user = User.query.get(g.user.id)
        user.username = request.form['username']
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.account_type = request.form['account_type']
        user.position = request.form['position']
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))


@app.route('/update', methods=['POST'])
def update_trash_counter():
    global trash_counter, personal_counter, this_beach, this_date, this_picked
    # Get the amount of trash picked up from the form
    picked_up = int(request.form['picked_up'])
    beach = request.form['beach']
    # trash_history = session.get('trash_history', [])
    # trash_history.append({
    #     'date': datetime.now().strftime('%Y-%m-%d'),
    #     'picked_up': picked_up,
    #     'beach': beach
    # })
    # session['trash_history'] = trash_history
    # session.modified = True  # Ensure session is saved
    # Update the trash counter
    this_picked = picked_up
    this_beach = beach

    trash_history.append({
        'date': datetime.now().strftime('%Y-%m-%d'),
        'picked_up': this_picked,
        'beach': this_beach
    })

    # this_date = datetime.now().strftime('%Y-%m-%d')
    trash_counter += picked_up
    personal_counter += picked_up
    # Redirect back to the main page
    return redirect(url_for('index'))

# @app.route('/update', methods=['POST'])
# def update_trash_counter():
#     picked_up = int(request.form['picked_up'])
#     beach = request.form['beach']
#     if beach == 'other':
#         other_beach = request.form['other_beach']
#         # Save the beach name to the database if it's not already there
#     trash_data = TrashData.query.first()  # Fetch the global total trash data
#     trash_data.total_trash_collected += picked_up  # Update global total trash data
#     db.session.commit()
#     user_id = session['user_id']
#     user = User.query.get(user_id)
#     user.personal_counter += picked_up  # Update user's personal counter
#     db.session.commit()
#     return redirect(url_for('index'))
