from datetime import datetime

from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm

from wtforms import DateField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange

from .models import db, Entry, User

insert_page = Blueprint("insert_page", __name__, template_folder="../templates")

class CompetitionForm(FlaskForm):

    date = DateField("Date",
        validators=[DataRequired()],
        default=datetime.today)
    w = IntegerField("W",
        validators=[DataRequired(), NumberRange(min=1, max=8)])
    p = IntegerField("P",
        validators=[DataRequired(), NumberRange(min=1, max=8)])
    n = IntegerField("N",
        validators=[DataRequired(), NumberRange(min=1, max=8)])
    user = SelectField("User")
    submit = SubmitField("Inserisci")

    def set_user_choices(self, users, default_user):
        # we put first the active user
        choices = [default_user.username]
        for user in users:
            if user.id != default_user.id:
                choices.append(user.username)
        self.user.choices = choices

@insert_page.route("/insert", methods=["GET", "POST"])
@login_required
def insert():
    users = User.query.all()
    form = CompetitionForm()
    form.set_user_choices(users, current_user)

    if form.validate_on_submit():
        username = form.user.data
        user_id = User.get_user_by_name(username).id

        existing_entry = Entry.query.filter_by(user_id=user_id, date=form.date.data).first()

        if existing_entry:
            existing_entry.w = form.w.data
            existing_entry.p = form.p.data
            existing_entry.n = form.n.data
            flash("Risultati aggiornati correttamente", "info")
        else:
            entry = Entry(
                user_id=user_id,
                date=form.date.data,
                w=form.w.data,
                p=form.p.data,
                n=form.n.data
            )
            db.session.add(entry)
            flash("Risultati inseriti correttamente", "success")

        db.session.commit()

        return redirect(url_for("insert_page.insert"))
    return render_template("insert.html", form=form, username=current_user.username)
