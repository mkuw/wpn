from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_login import login_user, logout_user, login_required
from passlib.hash import sha256_crypt
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired

from .models import User

login_page = Blueprint("login_page", __name__, template_folder="../templates")
logout_page = Blueprint("logout_page", __name__, template_folder="../templates")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    remember = BooleanField("Remember me")

@login_page.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and sha256_crypt.verify(form.password.data, user.password):
            login_user(user, remember=form.remember.data)
            flash("Login successful!", "success")
            return redirect(url_for("insert_page.insert"))

        flash("Invalid username or password", "danger")

    return render_template("login.html", form=form)

@logout_page.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "POST":
        logout_user()
        flash("You have been logged out", "success")
        return redirect(url_for("login_page.login"))
    return render_template("logout.html")
