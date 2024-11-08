from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash

import sqlite3
from datetime import datetime, date

app = Flask(__name__)


# ユーザークラスの定義
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email


# データベース初期化の更新
def init_db():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        # ユーザーテーブルを作成
        c.execute("""
            CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             username TEXT NOT NULL UNIQUE,
             email TEXT NOT NULL UNIQUE,
             password_hash TEXT NOT NULL)
        """)

        # カテゴリテーブルにuser_idを追加
        c.execute("""
            CREATE TABLE IF NOT EXISTS categories
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             color TEXT DEFAULT '#808080',
             user_id INTEGER NOT NULL,
             FOREIGN KEY (user_id) REFERENCES users (id),
             UNIQUE(name, user_id))
        """)

        # タスクテーブルにuser_idを追加
        c.execute("""
            CREATE TABLE IF NOT EXISTS tasks
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             title TEXT NOT NULL,
             description TEXT,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             completed BOOLEAN DEFAULT 0,
             due_date DATE,
             category_id INTEGER,
             user_id INTEGER NOT NULL,
             FOREIGN KEY (category_id) REFERENCES categories (id),
             FOREIGN KEY (user_id) REFERENCES users (id))
        """)
        conn.commit()


app.secret_key = "your-secret-key-here"  # 本番環境では安全な値に変更してください
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = c.fetchone()
        if user_data:
            return User(user_data[0], user_data[1], user_data[2])
    return None


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        with sqlite3.connect("tasks.db") as conn:
            c = conn.cursor()
            try:
                c.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, generate_password_hash(password)),
                )
                conn.commit()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("ユーザー名またはメールアドレスが既に使用されています")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect("tasks.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_data = c.fetchone()

            if user_data and check_password_hash(user_data[3], password):
                user = User(user_data[0], user_data[1], user_data[2])
                login_user(user)
                return redirect(url_for("index"))
            flash("ユーザー名またはパスワードが正しくありません")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


with app.app_context():
    init_db()


def get_task(id):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id = ?", (id,))
        return c.fetchone()


def get_categories():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM categories ORDER BY name")
        return c.fetchall()


@app.route("/categories")
def list_categories():
    categories = get_categories()
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["POST"])
@login_required
def add_category():
    name = request.form["name"]
    color = request.form["color"]
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO categories (name, color, user_id) VALUES (?, ?, ?)",
                (name, color, current_user.id),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("カテゴリ名が既に存在します")
    return redirect(url_for("list_categories"))


@app.route("/edit_category/<int:id>", methods=["GET", "POST"])
@login_required
def edit_category(id):
    if request.method == "POST":
        name = request.form["name"]
        color = request.form["color"]
        with sqlite3.connect("tasks.db") as conn:
            c = conn.cursor()
            c.execute(
                "UPDATE categories SET name = ?, color = ? WHERE id = ?",
                (name, color, id),
            )
            conn.commit()
        return redirect(url_for("list_categories"))

    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM categories WHERE id = ?", (id,))
        category = c.fetchone()
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<int:id>")
@login_required
def delete_category(id):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        # カテゴリを削除する前に、関連するタスクのcategory_idをNULLに設定
        c.execute("UPDATE tasks SET category_id = NULL WHERE category_id = ?", (id,))
        c.execute("DELETE FROM categories WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for("list_categories"))


@app.route("/")
@login_required
def index():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT t.*, c.name, c.color 
            FROM tasks t 
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
            ORDER BY t.due_date ASC, t.created_at DESC
        """,
            (current_user.id,),
        )
        tasks = c.fetchall()

    categories = get_categories()
    today = date.today()
    tasks_with_status = []
    for task in tasks:
        is_overdue = False
        if task[5] and not task[4]:
            due_date = datetime.strptime(task[5], "%Y-%m-%d").date()
            is_overdue = due_date < today
        tasks_with_status.append((task, is_overdue))

    return render_template("index.html", tasks=tasks_with_status, categories=categories)


@app.route("/add_task", methods=["POST"])
@login_required
def add_task():
    title = request.form["title"]
    description = request.form["description"]
    due_date = request.form["due_date"] or None
    category_id = request.form["category_id"] or None

    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO tasks (title, description, due_date, category_id, user_id)
            VALUES (?, ?, ?, ?, ?)
        """,
            (title, description, due_date, category_id, current_user.id),
        )
        conn.commit()
    return redirect(url_for("index"))


@app.route("/complete_task/<int:id>")
@login_required
def complete_task(id):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for("index"))


@app.route("/delete_task/<int:id>")
@login_required
def delete_task(id):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for("index"))


@app.route("/edit_task/<int:id>", methods=["GET", "POST"])
@login_required
def edit_task(id):
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        due_date = request.form["due_date"] or None
        category_id = request.form["category_id"] or None

        with sqlite3.connect("tasks.db") as conn:
            c = conn.cursor()
            c.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, due_date = ?, category_id = ? , user_id = ?
                WHERE id = ?
            """,
                (title, description, due_date, category_id, id),
            )
            conn.commit()
        return redirect(url_for("index"))

    task = get_task(id)
    categories = get_categories()
    return render_template("edit.html", task=task, categories=categories)


if __name__ == "__main__":
    app.run(debug=True)
