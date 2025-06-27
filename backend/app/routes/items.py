from flask import Blueprint, current_app, jsonify, request, abort
from sqlalchemy import select
from ..models import Item

bp = Blueprint("items_api", __name__, url_prefix="/api/items")


@bp.get("")
def list_items():
    with current_app.session() as s:
        rows = s.scalars(select(Item).order_by(Item.id)).all()
    return jsonify([r.to_dict() for r in rows])


@bp.post("")
def add_item():
    data = request.json or {}
    if not data.get("title"):
        abort(400, "title is required")
    item = Item(title=data["title"], description=data.get("description"))
    with current_app.session() as s:
        s.add(item)
        s.commit()
        s.refresh(item)
    return jsonify(item.to_dict()), 201


@bp.delete("/<int:item_id>")
def delete_item(item_id: int):
    with current_app.session() as s:
        item = s.get(Item, item_id)
        if not item:
            abort(404)
        s.delete(item)
        s.commit()
    return "", 204
