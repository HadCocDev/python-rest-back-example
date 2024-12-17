import unittest
from app import create_app
from models.database import db
from models.user import User
from models.facture import Facture
from datetime import datetime, timezone

class FactureTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            user = User(name="John Doe", email="john@example.com")
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_assign_facture_success(self):
        """Test la création réussie d'une facture pour un utilisateur existant."""
        payload = {
            "amount": 150.75,
            "description": "Service de consultation"
        }
        response = self.client.post(f"/api/users/{self.user_id}/factures", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["amount"], 150.75)
        self.assertEqual(data["description"], "Service de consultation")
        self.assertEqual(data["user_id"], self.user_id)
        self.assertIn("date", data) 

    def test_assign_facture_user_not_found(self):
        """Test la réponse lorsque l'utilisateur n'existe pas."""
        payload = {
            "amount": 150.75,
            "description": "Service de consultation"
        }
        response = self.client.post("/api/users/999/factures", json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.get_data(as_text=True))

    def test_modify_facture_success(self):
        """Test la modification réussie d'une facture existante."""
        payload = {
            "amount": 200.00,
            "description": "Initial Consultation"
        }
        post_response = self.client.post(f"/api/users/{self.user_id}/factures", json=payload)
        self.assertEqual(post_response.status_code, 201)
        facture_id = post_response.get_json()["id"]

        update_payload = {
            "amount": 250.00,
            "description": "Updated Consultation"
        }
        put_response = self.client.put(f"/api/users/{self.user_id}/factures/{facture_id}", json=update_payload)
        self.assertEqual(put_response.status_code, 200)
        data = put_response.get_json()
        self.assertEqual(data["amount"], 250.00)
        self.assertEqual(data["description"], "Updated Consultation")

if __name__ == "__main__":
    unittest.main()
