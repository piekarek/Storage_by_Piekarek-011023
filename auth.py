from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import User, db
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from flask_mail import Mail, Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app



auth = Blueprint('auth', __name__)
mail = Mail()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Redirect to the main index if already logged in
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=remember)
        return redirect(url_for('index'))  # Redirect to the main index after successful login
    return render_template('login.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email address already exists.')
            return redirect(url_for('auth.signup'))

        new_user = User(email=email, name=name)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Thanks for registering! Your account is pending approval by an admin.')
        return redirect(url_for('auth.login'))
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view

@auth.route('/manage_users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@auth.route('/toggle_approval/<int:user_id>', methods=['POST'])
@admin_required
def toggle_approval(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('Benutzer nicht gefunden.')
        return redirect(url_for('auth.manage_users'))

    user.is_approved = not user.is_approved
    db.session.commit()

    flash(f"Genehmigungsstatus für {user.name} geändert.")
    return redirect(url_for('auth.manage_users'))

@auth.route('/toggle_admin/<int:user_id>', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('Benutzer nicht gefunden.')
        return redirect(url_for('auth.manage_users'))

    user.is_admin = not user.is_admin
    db.session.commit()

    flash(f"Admin-Status für {user.name} geändert.")
    return redirect(url_for('auth.manage_users'))

@auth.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('Benutzer nicht gefunden.')
        return redirect(url_for('auth.manage_users'))

    db.session.delete(user)
    db.session.commit()

    flash(f"Benutzer {user.name} gelöscht.")
    return redirect(url_for('auth.manage_users'))


@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user:
            token = user.get_reset_token()
            msg = Message('Password Reset Request',
                          sender='noreply@yourdomain.com',
                          recipients=[user.email])
            msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}
'''
            mail.send(msg)
            flash('An email has been sent with instructions to reset your password.', 'info')
        else:
            flash('Email not found in the database.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html')

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
        user.set_password(password)
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', token=token)

@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Check if email already exists and is not the current user's email
    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.id != current_user.id:
        flash('This email is already associated with another account.', 'danger')
        return redirect(url_for('auth.profile'))

    # Check if new password fields are filled and match
    if password and confirm_password and password == confirm_password:
        current_user.set_password(password)
    elif password or confirm_password:
        flash('Passwords do not match!', 'danger')
        return redirect(url_for('auth.profile'))

    current_user.name = name
    current_user.email = email
    db.session.commit()

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile'))

