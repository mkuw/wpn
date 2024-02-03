from flask import Blueprint, render_template
from flask_login import login_required

from .models import Season, SeasonService

leaderboard_page = Blueprint("leaderboard_page", __name__, template_folder="../templates")

@leaderboard_page.route("/leaderboard", methods=["GET", "POST"])
@login_required
def leaderboard():
    seasons = [SeasonService(season) for season in Season.get_all_season()]
    for season in seasons:
        print(season.get_title())
        print(season.get_start_end_dates())
        print(season.get_leaderboard())
    return render_template("leaderboard.html")
