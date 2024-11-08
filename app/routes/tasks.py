from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ..models.task import Task
from ..models.category import Category
from datetime import datetime

bp = Blueprint("tasks", __name__)


@bp.route("/")
@login_required
def index():
    tasks = Task.get_all_by_user(current_user.id)
    categories = Category.get_all_by_user(current_user.id)
    return render_template("tasks/index.html", tasks=tasks, categories=categories)


@bp.route("/add", methods=["POST"])
@login_required
def add():
    title = request.form["title"]
    description = request.form["description"]
    due_date = request.form["due_date"] or None
    category_id = request.form["category_id"] or None

    Task.create(title, description, due_date, category_id, current_user.id)
    flash("タスクを追加しました")
    return redirect(url_for("tasks.index"))


@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    task = Task.get(id)
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        due_date = request.form["due_date"] or None
        category_id = request.form["category_id"] or None

        Task.update(id, title, description, due_date, category_id)
        flash("タスクを更新しました")
        return redirect(url_for("tasks.index"))

    categories = Category.get_all_by_user(current_user.id)
    return render_template("tasks/edit.html", task=task, categories=categories)


@bp.route("/complete/<int:id>")
@login_required
def complete(id):
    Task.complete(id)
    flash("タスクを完了としてマークしました")
    return redirect(url_for("tasks.index"))


@bp.route("/delete/<int:id>")
@login_required
def delete(id):
    Task.delete(id)
    flash("タスクを削除しました")
    return redirect(url_for("tasks.index"))
