# app.py
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired
from passlib.hash import sha256_crypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

def load_secret_key(filename='secret_key.txt'):
    try:
        with open(filename, 'r') as file:
            secret_key = file.read().strip()
            return secret_key
    except FileNotFoundError:
        print(f"Error: Secret key file '{filename}' not found.")
        return None

app = Flask(__name__)
app.config['SECRET_KEY'] = load_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database for simplicity
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    # Required for Flask-Login
    def is_active(self):
        return self.is_enabled

# Define the InviteCode model
class InviteCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)

# Define the RegistrationForm
class RegistrationForm(FlaskForm):
    invite_code = StringField('Invite Code', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    remember = BooleanField('Remember me')

# Define the route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Check if the invite code is valid
        if is_valid_invite_code(form.invite_code.data):
            # Hash the password before storing it in the database
            hashed_password = sha256_crypt.hash(form.password.data)

            # Create a new user
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            # Remove the used invite code from the database
            remove_invite_code(form.invite_code.data)

            flash('Your account has been created!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid invite code', 'danger')

    return render_template('register.html', form=form)

# Define the function to remove the used invite code
def remove_invite_code(invite_code):
    invite_code_entry = InviteCode.query.filter_by(code=invite_code).first()
    if invite_code_entry:
        db.session.delete(invite_code_entry)
        db.session.commit()

# Define the route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and sha256_crypt.verify(form.password.data, user.password):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Update with your dashboard route

        flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define a route for the dashboard (example)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

# Define a route for logout (example)
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'POST':
        logout_user()
        flash('You have been logged out', 'success')
        return redirect(url_for('login'))
    return render_template('logout.html')

# Define the function to check if the invite code is valid
def is_valid_invite_code(invite_code):
    return InviteCode.query.filter_by(code=invite_code).first() is not None

# Define a route for the default page
@app.route('/')
def default_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        login_manager.init_app(app)
    app.run(debug=True)
