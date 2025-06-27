from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)

@bp.get("/")
def root():
    return render_template("items.html")

@bp.get("/items")
def items_page():
    return render_template("items.html")
