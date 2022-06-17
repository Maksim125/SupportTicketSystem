from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, getenv
from flask_login import LoginManager
from dotenv import load_dotenv

db = SQLAlchemy()
DB_NAME = "database.db"
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app(config = None):
    app = Flask(__name__)
    load_dotenv()
    if not config:
        app.config['SECRET_KEY'] = getenv("SECRET_KEY")
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
        app.config["BASEDIR"] = path.abspath(path.dirname(__file__))
    if config:
        for key, value in config.items():
            app.config[key] = value
            
    create_database(app)
    initialize(app)
    register_blueprints(app)
    
    return app

def initialize(app):
    db.init_app(app)
    login_manager.init_app(app)
    from .models import User
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

def register_blueprints(app):
    from .views import views
    from .auth import auth
    from .request_endpoints import request_endpoints

    app.register_blueprint(views, url_prefix = "/")
    app.register_blueprint(auth, url_prefix = "/")
    app.register_blueprint(request_endpoints, url_prefix = "/")

def create_database(app):
    '''Create db if it does not exist already'''
    if not path.exists("SupportTicketSystem/" + DB_NAME):
        db.create_all(app = app)
        print("Created Datbase")