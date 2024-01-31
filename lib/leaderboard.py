from flask import Blueprint, render_template
from flask_login import login_required

from .models import get_all_season, get_podium

leaderboard_page = Blueprint("leaderboard_page", __name__, template_folder="../templates")

@leaderboard_page.route("/leaderboard", methods=["GET", "POST"])
@login_required
def leaderboard():
    seasons = get_all_season()
    for season in seasons:
        print(season.title)
        print(season.start_date)
        print(season.end_date)
        print(get_podium(season))
    return render_template("leaderboard.html")
