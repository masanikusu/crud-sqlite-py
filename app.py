# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, date

app = Flask(__name__)


def init_db():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS tasks
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             title TEXT NOT NULL,
             description TEXT,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             completed BOOLEAN DEFAULT 0,
             due_date DATE)
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


@app.route("/")
def index():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM tasks ORDER BY due_date, created_at DESC")
        tasks = c.fetchall()

    # 期限切れかどうかの情報を追加
    today = date.today()
    task_with_status = []
    for task in tasks:
        is_overdue = False
        if task[5] and not task[4]:
            due_date = datetime.strptime(task[5], "%Y-%m-%d").date()
            is_overdue = due_date < today
        task_with_status.append((task, is_overdue))

    return render_template("index.html", tasks=task_with_status)


@app.route("/add_task", methods=["POST"])
def add_task():
    title = request.form["title"]
    description = request.form["description"]
    due_date = request.form["due_date"] or None

    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO tasks (title, description, due_date) VALUES (?, ?, ?)",
            (title, description, due_date),
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

        with sqlite3.connect("tasks.db") as conn:
            c = conn.cursor()
            c.execute(
                "UPDATE tasks SET title = ?, description = ? due_date = ? WHERE id = ? ",
                (title, description, due_date, id),
            )
            conn.commit()
        return redirect(url_for("index"))

    task = get_task(id)
    return render_template("edit.html", task=task)


if __name__ == "__main__":
    app.run(debug=True)
