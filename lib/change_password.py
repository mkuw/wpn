from flask import Blueprint, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from passlib.hash import sha256_crypt
from wtforms import PasswordField
from wtforms.validators import InputRequired

from .models import db

change_password_page = Blueprint("change_password_page", __name__, template_folder="../templates")

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Vecchia Password", validators=[InputRequired()])
    new_password = PasswordField("Nuova Password", validators=[InputRequired()])
    confirm_password = PasswordField("Conferma Nuova Password", validators=[InputRequired()])

@change_password_page.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        user = current_user

        if user and sha256_crypt.verify(form.old_password.data, user.password):
            if form.new_password.data != form.confirm_password.data:
                flash("Le nuove password non coincidono.", "danger")
            else:
                hashed_password = sha256_crypt.hash(form.new_password.data)
                user.password = hashed_password
                db.session.commit()
                flash("Password cambiata con successo", "success")
                return redirect(url_for("change_password_page.change_password"))
        else:
            flash("La vecchia password non è corretta", "danger")

    return render_template("change_password.html", form=form)
