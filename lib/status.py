import datetime

from flask import Blueprint, render_template
from flask_login import login_required

from .models import Season, get_entries_for_season, get_user_by_id

status_page = Blueprint("status_page", __name__, template_folder="../templates")

def get_users_in_competition(entries):
    users = set()
    for entry in entries:
        users.add(get_user_by_id(entry.user_id).username)
    return list(users)

def get_season_days(season):
    delta = season.end_date - season.start_date
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

    print(season_entries)

    table_data = []
    for day in days:
        date_string = day.strftime("%d/%m")
        set_date = False
        for username in users:
            row = []
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
            row.append(p)
            row.append(n)
            row.append(w + p + n)
            row.append(w + p + n - 12)
            table_data.append(row)

    # Prepare data for the template
    # table_data = []
    # for user in users:
    #     user_row = [user.username]
    #     for entry in entries:
    #         user_entry = user_entries.get(user.id, {}).get(entry.date)
    #         user_row.append(user_entry.w if user_entry else 8)
    #     user_row.append(user_totals.get(user.id, 0))
    #     table_data.append(user_row)

    return render_template("status.html", table_data=table_data)
