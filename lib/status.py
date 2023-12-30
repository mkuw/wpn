import datetime
import numpy as np

from flask import Blueprint, render_template
from flask_login import login_required

import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .models import Season, get_entries_for_season, get_user_by_id

status_page = Blueprint("status_page", __name__, template_folder="../templates")

def get_users_in_competition(entries):
    users = set()
    for entry in entries:
        users.add(get_user_by_id(entry.user_id).username)
    return list(users)

def get_season_days(season):
    end_date = min(season.end_date, datetime.date.today())
    delta = end_date - season.start_date
    datetime_list = [season.start_date + datetime.timedelta(days=i) for i in range(delta.days + 1)]
    return datetime_list

@status_page.route('/status', methods=['GET', 'POST'])
@login_required
def status():
    season = Season.get_current_season()
    entries = get_entries_for_season(season)

    users = get_users_in_competition(entries)
    days = get_season_days(season)

    season_entries = {}
    for entry in entries:
        date_string = entry.date.strftime("%d/%m")
        username = get_user_by_id(entry.user_id).username
        season_entries[f"{date_string}_{username}"] = entry

    points_by_user = {}
    for user in users:
        points_by_user[user] = []

    table_data = []
    table_colors = []
    for day in days:
        date_string = day.strftime("%d/%m")
        set_date = False
        for username in users:
            row = []
            row_colors = ["normal", "normal"]
            if not set_date:
                row.append(date_string)
                set_date = True
            else:
                row.append("")
            row.append(username)
            key = f"{date_string}_{username}"
            if key in season_entries:
                entry = season_entries[key]
                w = entry.w
                p = entry.p
                n = entry.n
            else:
                w = 8
                p = 8
                n = 8
            row.append(w)
            if w == 8:
                row_colors.append("bad")
            elif w <= 2:
                row_colors.append("good")
            else:
                row_colors.append("normal")
            row.append(p)
            if p == 8:
                row_colors.append("bad")
            elif p <= 2:
                row_colors.append("good")
            else:
                row_colors.append("normal")
            row.append(n)
            if n == 8:
                row_colors.append("bad")
            elif n <= 2:
                row_colors.append("good")
            else:
                row_colors.append("normal")

            total = w + p + n
            row.append(total)
            row_colors.append("normal")

            key = day.strftime("%d/%m/%Y")
            if key in season.multipliers:
                multiplier = season.multipliers[key]
            else:
                multiplier = 1.0
            if multiplier > 1.0:
                row_colors.append("bad")
            else:
                row_colors.append("normal")
            row.append(multiplier)

            if total == 24:
                row_colors.append("bad")
            else:
                row_colors.append("normal")
            points = (w + p + n)*multiplier
            row.append(points)
            table_data.append(row)
            table_colors.append(row_colors)

            points_by_user[username].append(points)

    fig = make_subplots(rows=1, cols=1)
    for username, data in points_by_user.items():
        data = np.array(data)
        data -= 12
        data = np.cumsum(data)
        fig.add_trace(go.Scatter(x=days, y=data, mode="lines", name=username))
    fig.update_layout(title_text='Montagne russe WPN', xaxis_title='Data', yaxis_title='Punti')

    plot_html = fig.to_html(full_html=False)

    totals = []
    for username, data in points_by_user.items():
        totals.append([sum(data), username])

    start_date = season.start_date.strftime("%d/%m")
    end_date = season.end_date.strftime("%d/%m")

    return render_template("status.html", title=season.title,
        table_data=table_data, table_colors=table_colors,
        plot_html=plot_html, total_table_data=sorted(totals),
        start_date=start_date, end_date=end_date)
