import unittest
from app import create_app
from models.database import db
from models.contract import Contract
from models.user import User 
from datetime import datetime, timedelta, timezone

class UserContractTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            user = User(name="Alice", email="alice@example.com")
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_user_contract_success(self):
        payload = {
            "contract_number": "CT-U-001",
            "start_date": datetime.now(timezone.utc).isoformat(),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            "terms": "Conditions contractuelles pour FIBRUS."
        }
        response = self.client.post(f"/users/{self.user_id}/contracts", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["contract_number"], payload["contract_number"])
        self.assertEqual(data["terms"], payload["terms"])
        self.assertIn("start_date", data)
        self.assertIn("end_date", data)
        self.assertEqual(data["user_id"], self.user_id)

    def test_create_user_contract_user_not_found(self):
        payload = {
            "contract_number": "CT-U-002",
            "start_date": datetime.now(timezone.utc).isoformat(),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            "terms": "Conditions contractuelles pour un user inexistant."
        }
        response = self.client.post("/users/999/contracts", json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.get_data(as_text=True))

    def test_get_user_contract_success(self):
        payload = {
            "contract_number": "CT-U-003",
            "start_date": datetime.now(timezone.utc).isoformat(),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=180)).isoformat(),
            "terms": "Contrat pour FIBRUS."
        }
        post_response = self.client.post(f"/users/{self.user_id}/contracts", json=payload)
        contract_id = post_response.get_json()["id"]

        get_response = self.client.get(f"/users/{self.user_id}/contracts/{contract_id}")
        self.assertEqual(get_response.status_code, 200)
        data = get_response.get_json()
        self.assertEqual(data["id"], contract_id)
        self.assertEqual(data["contract_number"], payload["contract_number"])

    def test_update_user_contract_success(self):
        payload = {
            "contract_number": "CT-U-004",
            "start_date": datetime.now(timezone.utc).isoformat(),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
            "terms": "Contrat initial pour FIBRUS."
        }
        post_response = self.client.post(f"/users/{self.user_id}/contracts", json=payload)
        contract_id = post_response.get_json()["id"]

        update_payload = {
            "contract_number": "CT-U-004-UPDATED",
            "terms": "Contrat mis à jour avec conditions révisées."
        }
        put_response = self.client.put(f"/users/{self.user_id}/contracts/{contract_id}", json=update_payload)
        self.assertEqual(put_response.status_code, 200)
        data = put_response.get_json()
        self.assertEqual(data["contract_number"], update_payload["contract_number"])
        self.assertEqual(data["terms"], update_payload["terms"])

    def test_delete_user_contract_success(self):
        payload = {
            "contract_number": "CT-U-005",
            "start_date": datetime.now(timezone.utc).isoformat(),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            "terms": "Contrat à supprimer pour FIBRUS."
        }
        post_response = self.client.post(f"/users/{self.user_id}/contracts", json=payload)
        contract_id = post_response.get_json()["id"]

        delete_response = self.client.delete(f"/users/{self.user_id}/contracts/{contract_id}")
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn("deleted", delete_response.get_data(as_text=True))

        get_response = self.client.get(f"/users/{self.user_id}/contracts/{contract_id}")
        self.assertEqual(get_response.status_code, 404)

if __name__ == "__main__":
    unittest.main()