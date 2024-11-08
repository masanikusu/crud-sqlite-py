from flask import Flask
from flask_login import LoginManager

from .models.user import User
from .utils.db import close_db
from .routes import auth, tasks, categories
from config import Config

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # データベース設定
    app.teardown_appcontext(close_db)

    # Blueprintの登録
    app.register_blueprint(auth.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(categories.bp)

    # Flask-Login設定
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    return app
