from ..utils.db import get_db


class Category:
    @staticmethod
    def create(name, color, user_id):
        db = get_db()
        try:
            db.execute(
                "INSERT INTO categories (name, color, user_id) VALUES (?,?,?)",
                (name, color, user_id),
            )
            db.commit()
            return True
        except db.IntegrityError:
            return False

    @staticmethod
    def get_all_by_user(user_id):
        db = get_db()
        return db.execute(
            "SELECT * FROM categories WHERE user_id = ? ORDER BY name", (user_id,)
        ).fetchall()

    @staticmethod
    def get(id):
        db = get_db()
        return db.execute("SELECT * FROM categories WHERE id = ?", (id,)).fetchone()

    @staticmethod
    def update(id, name, color):
        db = get_db()
        try:
            db.execute(
                "UPDATE categories SET name = ?, color = ? WHERE id = ?",
                (name, color, id),
            )
            db.commit()
            return True
        except db.IntegrityError:
            return False

    @staticmethod
    def delete(id):
        db = get_db()
        db.execute("UPDATE tasks SET category_id = NULL WHERE category_id = ?", (id,))
        db.execute("DELETE FROM categories WHERE id = ?", (id,))
        db.commit()
