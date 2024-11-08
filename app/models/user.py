from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils.db import get_db


class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        
        if user is None:
            return None
            
        return User(
            id=user['id'],
            username=user['username'],
            password_hash=user['password_hash']
        )

    @staticmethod
    def create(username, email, password):
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?,?,?)",
                (username, email, generate_password_hash(password)),
            )
            db.commit()
            return True
        except db.IntegrityError:
            return False

    @staticmethod
    def authenticate(username, password):
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            return User(user["id"], user["username"], user["email"])
        return None
