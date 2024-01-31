from flask import Flask
from lib.utils import load_secret_key

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = load_secret_key()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

    # register the database
    from .models import db
    db.init_app(app)

    # register the various pages
    from .register import register_page
    app.register_blueprint(register_page, url_prefix="/")

    from .login_logout import login_page, logout_page
    app.register_blueprint(login_page, url_prefix="/")
    app.register_blueprint(logout_page, url_prefix="/")

    from .insert import insert_page
    app.register_blueprint(insert_page, url_prefix="/")

    from .status import status_page
    app.register_blueprint(status_page, url_prefix="/")

    from .leaderboard import leaderboard_page
    app.register_blueprint(leaderboard_page, url_prefix="/")

    return app

def print_routes(app):
    print("All Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.methods} {rule}")
