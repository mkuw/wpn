import datetime
import numpy as np

from flask import Blueprint, render_template, request
from flask_login import login_required

import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .models import Season, SeasonService

status_page = Blueprint("status_page", __name__, template_folder="../templates")

@status_page.route('/status', methods=['GET', 'POST'])
@login_required
def status():
    query_date = request.args.get('date')
    if query_date:
        date = datetime.datetime.strptime(query_date, '%d/%m/%Y').date()
        season = SeasonService(Season.get_season_by_date(date))
    else:
        season = SeasonService(Season.get_current_season())

    if season.is_none():
        return render_template("no_season.html")
    entries = season.get_entries_dictionary()

    users = season.get_users_in_competition()
    season_days = season.get_season_days()
    multipliers = season.get_multipliers()

    points_by_user = {}
    for user in users:
        points_by_user[user] = []

    table_data = []
    table_colors = []
    for multiplier, day in zip(multipliers, season_days):
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
            if key in entries:
                entry = entries[key]
                w = entry.w
                p = entry.p
                n = entry.n
                colors = []
                for value in [w, p, n]:
                    if value >= 6:
                        colors.append("bad")
                    elif value <= 2:
                        colors.append("good")
                    else:
                        colors.append("normal")
            elif day < datetime.date.today():
                entry = season.get_penalty(day, username)
                w = entry.w
                p = entry.p
                n = entry.n
                colors = ["missing", "missing", "missing"]
            else:
                w = np.nan
                p = np.nan
                n = np.nan
                colors = ["normal", "normal", "normal"]

            if np.isnan(w):
                row.append("")
            else:
                row.append(f"{w:d}")
            if np.isnan(p):
                row.append("")
            else:
                row.append(f"{p:d}")
            if np.isnan(n):
                row.append("")
            else:
                row.append(f"{n:d}")

            row_colors.extend(colors)

            # total
            total = w + p + n
            if np.isnan(total):
                row.append("")
                row_colors.append("normal")
            else:
                row.append(f"{total:d}")
                if total > 20:
                    row_colors.append("bad")
                else:
                    row_colors.append("normal")

            m = min(int((multiplier - 1.0)*10) + 1, 10)
            row.append(f"{multiplier:6.3f}")
            row_colors.append(f"m{m}")

            row_colors.append("normal")
            points = (w + p + n)*multiplier
            if np.isnan(points):
                row.append("")
            else:
                row.append(f"{points:6.3f}")

            table_data.append(row)
            table_colors.append(row_colors)

            points_by_user[username].append(points)

    fig = make_subplots(rows=1, cols=1)
    multipliers = np.array(multipliers)
    for username, data in points_by_user.items():
        data = np.array(data)
        data -= 12*multipliers
        data = np.cumsum(data)
        fig.add_trace(go.Scatter(x=season_days, y=data, mode="lines+markers", name=username))
    fig.update_layout(title_text='Montagne russe WPN', xaxis_title='Data',
        yaxis_title='Punti')

    plot_html = fig.to_html(full_html=False)

    totals = []
    for username, data in points_by_user.items():
        data = np.nan_to_num(data)
        total = sum(data)
        totals.append([f"{total:6.3f}", username])

    start_date, end_date = season.get_start_end_dates()
    title = season.get_title()

    return render_template("status.html", title=title,
        table_data=table_data, table_colors=table_colors,
        plot_html=plot_html, total_table_data=sorted(totals),
        start_date=start_date, end_date=end_date)
