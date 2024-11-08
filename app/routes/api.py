from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import login_required, login_user, logout_user, current_user

from ..models.user import User
from ..models.task import Task
from ..models.category import Category

bp = Blueprint("api", __name__, url_prefix="/api")


# 認証関連のエンドポイント
@bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    try:
        user = User.create(
            username=data["username"], email=data["email"], password=data["password"]
        )
        return jsonify({"status": "success", "message": "ユーザー登録が完了しました"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.authenticate(data["username"], data["password"])
    if user:
        login_user(user)
        return jsonify(
            {
                "status": "success",
                "user": {"id": user.id, "username": user.username, "email": user.email},
            }
        )
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


@bp.route("/auth/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"status": "success"})


@bp.route("/auth/user")
@login_required
def user():
    return jsonify(
        {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
        }
    )


# タスク関連のエンドポイント
@bp.route("/tasks")
@login_required
def get_tasks():
    tasks = Task.get_all_by_user(current_user.id)
    return jsonify([dict(task) for task in tasks])


@bp.route("/tasks/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    task = Task.get(task_id)
    if task and task["user_id"] == current_user.id:
        return jsonify(dict(task))
    return jsonify({"status": "error", "message": "Task not found"}), 404


@bp.route("/tasks", methods=["POST"])
@login_required
def create_task():
    data = request.get_json()
    try:
        task = Task.create(
            title=data["title"],
            description=data.get("description"),
            due_date=datetime.strptime(data["due_date"], "%Y-%m-%d").date()
            if data.get("due_date")
            else None,
            category_id=data.get("category_id"),
            user_id=current_user.id,
        )
        return jsonify(dict(task))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@bp.route("/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    data = request.get_json()
    task = Task.get(task_id)

    if not task or task["user_id"] != current_user.id:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    try:
        updated_task = Task.update(
            id=task_id,
            title=data.get("title", task["title"]),
            description=data.get("description", task["description"]),
            due_date=datetime.strptime(data["due_date"], "%Y-%m-%d").date()
            if data.get("due_date")
            else None,
            category_id=data.get("category_id", task["category_id"]),
        )
        return jsonify(dict(updated_task))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    task = Task.get(task_id)
    if not task or task["user_id"] != current_user.id:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    Task.delete(task_id)
    return jsonify({"status": "success"})


@bp.route("/tasks/<int:task_id>/complete", methods=["POST"])
@login_required
def complete_task(task_id):
    task = Task.get(task_id)
    if not task or task["user_id"] != current_user.id:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    Task.complete(task_id)
    return jsonify({"status": "success"})


# カテゴリ関連のエンドポイント
@bp.route("/categories", methods=["GET"])
@login_required
def get_categories():
    categories = Category.get_all_by_user(current_user.id)
    return jsonify([dict(category) for category in categories])


@bp.route("/categories/<int:category_id>", methods=["GET"])
@login_required
def get_category(category_id):
    category = Category.get(category_id)
    if category and category["user_id"] == current_user.id:
        return jsonify(dict(category))
    return jsonify({"status": "error", "message": "Category not found"}), 404


@bp.route("/categories", methods=["POST"])
@login_required
def create_category():
    data = request.get_json()
    try:
        category = Category.create(
            name=data["name"],
            color=data.get("color", "#808080"),
            user_id=current_user.id,
        )
        return jsonify(dict(category))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@bp.route("/categories/<int:category_id>", methods=["PUT"])
@login_required
def update_category(category_id):
    data = request.get_json()
    category = Category.get(category_id)

    if not category or category["user_id"] != current_user.id:
        return jsonify({"status": "error", "message": "Category not found"}), 404

    try:
        updated_category = Category.update(
            id=category_id,
            name=data.get("name", category["name"]),
            color=data.get("color", category["color"]),
        )
        return jsonify(dict(updated_category))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@bp.route("/categories/<int:category_id>", methods=["DELETE"])
@login_required
def delete_category(category_id):
    category = Category.get(category_id)
    if not category or category["user_id"] != current_user.id:
        return jsonify({"status": "error", "message": "Category not found"}), 404

    Category.delete(category_id)
    return jsonify({"status": "success"})


# エラーハンドリング
@bp.errorhandler(404)
def not_found_error(error):
    return jsonify({"status": "error", "message": "Resource not found"}), 404


@bp.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Internal server error"}), 500
