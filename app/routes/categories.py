from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ..models.category import Category

bp = Blueprint("categories", __name__, url_prefix="/categories")


@bp.route("/")
@login_required
def index():
    categories = Category.get_all_by_user(current_user.id)
    return render_template("categories/index.html", categories=categories)


@bp.route("/add", methods=["POST"])
@login_required
def add():
    name = request.form["name"]
    color = request.form["color"]

    if Category.create(name, color, current_user.id):
        flash("カテゴリを追加しました")
    else:
        flash("カテゴリ名が既に存在します")
    return redirect(url_for("categories.index"))


@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    category = Category.get(id)

    if request.method == "POST":
        name = request.form["name"]
        color = request.form["color"]

        if Category.update(id, name, color):
            flash("カテゴリを更新しました")
            return redirect(url_for("categories.index"))
        flash("カテゴリ名が既に存在します")

    return render_template("categories/edit.html", category=category)


@bp.route("/delete/<int:id>")
@login_required
def delete(id):
    Category.delete(id)
    flash("カテゴリを削除しました")
    return redirect(url_for("categories.index"))
