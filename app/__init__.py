from flask import Flask
from .database import db
from config import Config

from .routes import main


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(main)

    db.init_app(app)
    return app
