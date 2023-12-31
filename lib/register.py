from flask import Blueprint, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from passlib.hash import sha256_crypt

from .models import db, User
from .utils import is_valid_invite_code, remove_invite_code

register_page = Blueprint("register_page", __name__, template_folder="../templates")

class RegistrationForm(FlaskForm):
    invite_code = StringField("Codice Invito", validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from passlib.hash import sha256_crypt

from .models import db, User
from .utils import is_valid_invite_code, remove_invite_code

register_page = Blueprint("register_page", __name__, template_folder="../templates")

class RegistrationForm(FlaskForm):
    invite_code = StringField("Codice Invito", validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

@register_page.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        if is_valid_invite_code(form.invite_code.data):
            # Check if the username already exists
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash("Username già esistente, sceglierne un altro", "danger")
            else:
                hashed_password = sha256_crypt.hash(form.password.data)

                # Create a new user
                new_user = User(username=form.username.data, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()

                # Remove the used invite code from the database
                remove_invite_code(form.invite_code.data, db)

                flash("Account creato con successo", "success")
                return redirect(url_for("login_page.login"))
        else:
            flash("Codice invito non valido", "danger")

    return render_template("register.html", form=form)
