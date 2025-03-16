from flask import Blueprint, request, jsonify
from models.database import db
from models.contract import Contract
from models.user import User
from datetime import datetime

contract_routes = Blueprint("contract_routes", __name__)

@contract_routes.route("/users/<int:user_id>/contracts", methods=["POST"])
def create_user_contract(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    required_fields = ["contract_number", "start_date", "end_date", "terms"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "contract_number, start_date, end_date and terms are required"}), 400

    try:
        start_date = datetime.fromisoformat(data["start_date"])
        end_date = datetime.fromisoformat(data["end_date"])
    except Exception:
        return jsonify({"error": "Dates must be in ISO format"}), 400

    new_contract = Contract(
        contract_number=data["contract_number"],
        start_date=start_date,
        end_date=end_date,
        terms=data["terms"],
        user_id=user_id
    )
    db.session.add(new_contract)
    db.session.commit()
    return jsonify(new_contract.to_dict()), 201

@contract_routes.route("/users/<int:user_id>/contracts/<int:contract_id>", methods=["GET"])
def get_user_contract(user_id, contract_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    contract = Contract.query.filter_by(id=contract_id, user_id=user_id).first()
    if not contract:
        return jsonify({"error": "Contract not found"}), 404
    return jsonify(contract.to_dict()), 200

@contract_routes.route("/users/<int:user_id>/contracts/<int:contract_id>", methods=["PUT"])
def update_user_contract(user_id, contract_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    contract = Contract.query.filter_by(id=contract_id, user_id=user_id).first()
    if not contract:
        return jsonify({"error": "Contract not found"}), 404

    data = request.get_json()
    allowed_fields = ["contract_number", "start_date", "end_date", "terms"]
    for field in data:
        if field not in allowed_fields:
            return jsonify({"error": f"Invalid field: {field}"}), 400

    if "contract_number" in data:
        contract.contract_number = data["contract_number"]
    if "start_date" in data:
        try:
            contract.start_date = datetime.fromisoformat(data["start_date"])
        except Exception:
            return jsonify({"error": "start_date must be in ISO format"}), 400
    if "end_date" in data:
        try:
            contract.end_date = datetime.fromisoformat(data["end_date"])
        except Exception:
            return jsonify({"error": "end_date must be in ISO format"}), 400
    if "terms" in data:
        contract.terms = data["terms"]

    db.session.commit()
    return jsonify(contract.to_dict()), 200

@contract_routes.route("/users/<int:user_id>/contracts/<int:contract_id>", methods=["DELETE"])
def delete_user_contract(user_id, contract_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    contract = Contract.query.filter_by(id=contract_id, user_id=user_id).first()
    if not contract:
        return jsonify({"error": "Contract not found"}), 404

    db.session.delete(contract)
    db.session.commit()
    return jsonify({"message": "Contract deleted successfully"}), 200