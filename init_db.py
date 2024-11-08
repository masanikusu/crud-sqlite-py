import os
import sqlite3
from app import create_app


def init_db():
    app = create_app()

    with app.app_context():
        # データベースディレクトリが存在しない場合は作成
        db_dir = os.path.dirname(app.config["DATABASE"])
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # データベースに接続してスキーマを実行
        with sqlite3.connect(app.config["DATABASE"]) as conn:
            with app.open_resource("schema.sql") as f:
                conn.executescript(f.read().decode("utf8"))

        print("データベースを初期化しました。")


if __name__ == "__main__":
    init_db()
