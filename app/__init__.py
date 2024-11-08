from flask import Flask, send_from_directory
from flask_login import LoginManager

from .models.user import User
from .utils.db import close_db
from .routes import api
from config import Config

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # データベース設定
    app.teardown_appcontext(close_db)

    # APIルートの登録
    app.register_blueprint(api.bp)

    # Flask-Login設定
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # SPAのメインルート
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path and path.startswith('api/'):
            return {'error': 'Not found'}, 404
        return send_from_directory(app.static_folder, 'index.html')

    return app
