from flask import Blueprint, render_template
from flask_login import current_user, login_required

dashboard_page = Blueprint("dashboard_page", __name__, template_folder="../templates")

# Define a route for the dashboard (example)
@dashboard_page.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)
