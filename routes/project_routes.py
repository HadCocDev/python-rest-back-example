from flask import Blueprint, request, jsonify
from models.database import db
from models.project import Project

project_routes = Blueprint("project_routes", __name__)

@project_routes.route("/projects", methods=["POST"])
def create_project():
    data = request.get_json()
    required_fields = ["title", "description"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Title and description are required"}), 400

    title = data["title"]
    description = data["description"]
    status = data.get("status", "active")

    new_project = Project(title=title, description=description, status=status)
    db.session.add(new_project)
    db.session.commit()

    return jsonify(new_project.to_dict()), 201

@project_routes.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(project.to_dict()), 200

@project_routes.route("/projects", methods=["GET"])
def list_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects]), 200

@project_routes.route("/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()
    allowed_fields = ["title", "description", "status"]

    for field in data:
        if field not in allowed_fields:
            return jsonify({"error": f"Invalid field: {field}"}), 400

    if "title" in data:
        project.title = data["title"]
    if "description" in data:
        project.description = data["description"]
    if "status" in data:
        project.status = data["status"]

    db.session.commit()
    return jsonify(project.to_dict()), 200

@project_routes.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted successfully"}), 200
