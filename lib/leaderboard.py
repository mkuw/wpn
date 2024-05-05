from flask import Blueprint, render_template
from flask_login import login_required

from .models import Season, SeasonService

leaderboard_page = Blueprint("leaderboard_page", __name__, template_folder="../templates")

class UserMedals:

    def __init__(self):
        self.users = set([])
        self.medals = {}

    def add(self, user, position):
        if user not in self.users:
            self.users.add(user)
            self.medals[user] = {
                "gold": 0,
                "silver": 0,
                "bronze": 0}
        if position == 1:
            self.medals[user]["gold"] += 1
        if position == 2:
            self.medals[user]["silver"] += 1
        if position == 3:
            self.medals[user]["bronze"] += 1

    def get_sorted_table(self):
        sorted_users = sorted(self.users, key=lambda user: (
            self.medals[user]["gold"],
            self.medals[user]["silver"],
            self.medals[user]["bronze"]
        ), reverse=True)

        result = []
        for user in sorted_users:
            medals = self.medals[user]
            result.append([user, medals["gold"], medals["silver"], medals["bronze"]])

        return result


@leaderboard_page.route("/leaderboard", methods=["GET", "POST"])
@login_required
def leaderboard():
    seasons = [SeasonService(season) for season in Season.get_all_season()]
    current_season = Season.get_current_season()

    users_medals = UserMedals()

    season_table = []
    for season in seasons:
        if current_season:
            if season.get_title() == current_season.title:
                continue
        row = []
        row.append(season.get_title())
        row.extend(season.get_start_end_dates())

        gold = []
        silver = []
        bronze = []
        season_leaderboard = season.get_leaderboard()
        for entry in season_leaderboard:
            if entry["position"] == 1:
                gold.append(entry["user"])
                users_medals.add(entry["user"], 1)
            if entry["position"] == 2:
                silver.append(entry["user"])
                users_medals.add(entry["user"], 2)
            if entry["position"] == 3:
                bronze.append(entry["user"])
                users_medals.add(entry["user"], 3)

        row.append(", ".join(gold))
        row.append(", ".join(silver))
        row.append(", ".join(bronze))

        season_table.append(row)

    user_table = users_medals.get_sorted_table()
    return render_template("leaderboard.html",
        season_table=season_table, user_table=user_table)
