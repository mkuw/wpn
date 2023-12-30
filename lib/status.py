from flask import Blueprint, render_template
from flask_login import login_required

status_page = Blueprint("status_page", __name__, template_folder="../templates")

@status_page.route('/status', methods=['GET', 'POST'])
@login_required
def status():
    return render_template('status.html')
