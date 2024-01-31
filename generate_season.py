#!/usr/bin/python

import datetime
import argparse

from flask import Flask
from lib.models import db, Season, get_season_by_title

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db.init_app(app)

def parse_args():
    parser = argparse.ArgumentParser(description="Aggiungi o modifica stagioni")
    parser.add_argument("titolo", type=str, nargs="+",
        help="Titolo univoco della stagione, se il titolo "
        "è già presente nel database, la stagione precedente "
        "verrà modificata.")
    parser.add_argument("--inizio", type=str, help="Data di inizio")
    parser.add_argument("--fine", type=str, help="Data di fine")
    parser.add_argument("--moltiplicatori", nargs="*", type=str,
        help='Sequenza di stringhe con data e moltiplicatore '
        'ad esempio "31/12/2023 2.0"')
    parser.add_argument("--elimina", action="store_true",
        help="Elimina la stagione.")
    args = parser.parse_args()
    args.titolo = " ".join(args.titolo)
    return args

def parse_date(date_string):
    return datetime.datetime.strptime(date_string, "%d/%m/%Y").date()

def modify_season(season, args):
    print("La stagione è già presente, verrà modificata")

def add_season(args):
    print("La stagione non è presente, verrà aggiunta")
    start_date = parse_date(args.inizio)
    end_date = parse_date(args.fine)
    multipliers = {}
    if args.moltiplicatori:
        for multiplier in args.moltiplicatori:
            tokens = multiplier.split()
            date = parse_date(tokens[0])
            factor = float(tokens[1])
            key = date.strftime("%d/%m/%Y")
            multipliers[key] = factor
    season = Season(title=args.titolo,
        start_date=start_date, end_date=end_date,
        multipliers=multipliers)
    db.session.add(season)
    db.session.commit()

def remove_season(season):
    print("La stagione verrà eliminata")
    db.session.delete(season)
    db.session.commit()

if __name__ == "__main__":
    args = parse_args()

    with app.app_context():
        db.create_all()
        season = get_season_by_title(args.titolo)
        if season:
            if args.elimina:
                remove_season(season)
            else:
                modify_season(season, args)
        else:
            add_season(args)
