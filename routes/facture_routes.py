from datetime import datetime
from flask import Blueprint, request, jsonify
from models.database import db
from models.user import User
from models.facture import Facture

facture_routes = Blueprint("facture_routes", __name__)

@facture_routes.route("/users/<int:user_id>/factures", methods=["POST"])
def assign_facture(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    required_fields = ["amount", "description"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Amount and description are required"}), 400

    try:
        amount = float(data["amount"])
        description = data["description"]
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data types for amount or description"}), 400

    new_facture = Facture(amount=amount, description=description, user_id=user_id)
    db.session.add(new_facture)
    db.session.commit()
    return jsonify(new_facture.to_dict()), 201

@facture_routes.route("/users/<int:user_id>/factures/<int:facture_id>", methods=["PUT"])
def modify_facture(user_id, facture_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    facture = Facture.query.filter_by(id=facture_id, user_id=user_id).first()
    if not facture:
        return jsonify({"error": "Facture not found for this user"}), 404

    data = request.get_json()
    allowed_fields = ["amount", "description", "date"]

    for field in data:
        if field not in allowed_fields:
            return jsonify({"error": f"Invalid field: {field}"}), 400

    if "amount" in data:
        try:
            facture.amount = float(data["amount"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid value for amount"}), 400

    if "description" in data:
        facture.description = data["description"]

    if "date" in data:
        try:
            facture.date = datetime.fromisoformat(data["date"])
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

    db.session.commit()
    return jsonify(facture.to_dict()), 200
