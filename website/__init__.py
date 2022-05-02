"""
Return the pathname of the KOS root directory.
"""

import time
from os import path
from flask import Blueprint, render_template, request, flash, jsonify
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = '../db/test_new.db'


def create_app():
    """Return the pathname of the KOS root directory."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{DB_NAME}'.format(DB_NAME=DB_NAME)
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(Id):
        """Return the pathname of the KOS root directory."""
        return User.query.get(int(Id))

    return app


def create_database(app):
    db.create_all(app=app)
