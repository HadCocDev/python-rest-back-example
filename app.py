# app.py
from flask import Flask
from models.database import db
from routes.user_routes import user_routes
from routes.facture_routes import facture_routes
from routes.project_routes import project_routes
from routes.contract_routes import contract_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()  # Creates database tables if they don't exist

    # Register blueprints
    app.register_blueprint(user_routes, url_prefix="/api")
    app.register_blueprint(facture_routes, url_prefix="/api")
    app.register_blueprint(project_routes, url_prefix="/api")
    app.register_blueprint(contract_routes, url_prefix="/api")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=3000)
