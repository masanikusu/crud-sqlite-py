# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, date

app = Flask(__name__)


def init_db():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        # カテゴリテーブルを作成
        c.execute("""
                  CREATE TABLE IF NOT EXISTS categories
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL UNIQUE,
                  color TEXT DEFAULT '#808080')
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS tasks
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             title TEXT NOT NULL,
             description TEXT,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             completed BOOLEAN DEFAULT 0,
             due_date DATE,
             category_id INTEGER,
             FOREIGN KEY (category_id) REFERENCES categories (id))
        """)
        conn.commit()


# before_first_requestの代わりにwith app.app_contextを使用
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
def add_category():
    name = request.form["name"]
    color = request.form["color"]
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO categories (name, color) VALUES (?, ?)", (name, color)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("カテゴリ名が既に存在します")
    return redirect(url_for("list_categories"))


@app.route("/edit_category/<int:id>", methods=["GET", "POST"])
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
def delete_category(id):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        # カテゴリを削除する前に、関連するタスクのcategory_idをNULLに設定
        c.execute("UPDATE tasks SET category_id = NULL WHERE category_id = ?", (id,))
        c.execute("DELETE FROM categories WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for("list_categories"))


@app.route("/")
def index():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute("""
            SELECT t.*, c.name, c.color 
            FROM tasks t 
            LEFT JOIN categories c ON t.category_id = c.id 
            ORDER BY t.due_date ASC, t.created_at DESC
        """)
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
def add_task():
    title = request.form["title"]
    description = request.form["description"]
    due_date = request.form["due_date"] or None
    category_id = request.form["category_id"] or None

    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO tasks (title, description, due_date, category_id) 
            VALUES (?, ?, ?, ?)
        """,
            (title, description, due_date, category_id),
        )
        conn.commit()
    return redirect(url_for("index"))


@app.route("/complete_task/<int:id>")
def complete_task(id):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for("index"))


@app.route("/delete_task/<int:id>")
def delete_task(id):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for("index"))


@app.route("/edit_task/<int:id>", methods=["GET", "POST"])
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
                SET title = ?, description = ?, due_date = ?, category_id = ? 
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
