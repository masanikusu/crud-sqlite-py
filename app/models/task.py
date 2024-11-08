from datetime import datetime

from ..utils.db import get_db


class Task:
    @staticmethod
    def create(title, description, due_date, category_id, user_id):
        db = get_db()
        db.execute(
            """
            INSERT INTO tasks (title, description, due_date, category_id, user_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, description, due_date, category_id, user_id)
        )
        db.commit()

    @staticmethod
    def get_all_by_user(user_id):
        db = get_db()
        return db.execute(
            """
            SELECT t.*, c.name as category_name, c.color as category_color
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
            ORDER BY t.due_date ASC, t.created_at DESC
        """,
            (user_id,)
        ).fetchall()

    @staticmethod
    def update(id, title, description, due_date, category_id):
        db = get_db()
        db.execute(
            """
            UPDATE tasks
            SET title = ?, 
                description = ?, 
                due_date = ?, 
                category_id = ?
            WHERE id = ?
            """,
            (title, description, due_date, category_id, id)
        )
        db.commit()

    @staticmethod
    def delete(id):
        db = get_db()
        db.execute("DELETE FROM tasks WHERE id = ?", (id,))
        db.commit()

    @staticmethod
    def complete(id):
        db = get_db()
        db.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (id,))
        db.commit()

    @staticmethod
    def get(id):
        db = get_db()
        return db.execute(
            """
            SELECT t.*, c.name as category_name, c.color as category_color
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.id = ?
            """,
            (id,)
        ).fetchone()
