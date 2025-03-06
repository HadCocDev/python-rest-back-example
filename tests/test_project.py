import unittest
from app import create_app
from models.database import db
from models.project import Project

class ProjectTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_project_success(self):
        payload = {
            "title": "Nouveau Projet",
            "description": "Développement de la nouvelle API pour FIBRUS"
        }
        response = self.client.post("/api/projects", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["title"], payload["title"])
        self.assertEqual(data["description"], payload["description"])
        self.assertEqual(data["status"], "active")

    def test_get_project_success(self):

        payload = {
            "title": "Projet Test",
            "description": "Description du projet test"
        }
        create_response = self.client.post("/api/projects", json=payload)
        project_id = create_response.get_json()["id"]

        get_response = self.client.get(f"/api/projects/{project_id}")
        self.assertEqual(get_response.status_code, 200)
        data = get_response.get_json()
        self.assertEqual(data["id"], project_id)

    def test_update_project_success(self):
        payload = {
            "title": "Projet Initial",
            "description": "Description initiale"
        }
        create_response = self.client.post("/api/projects", json=payload)
        project_id = create_response.get_json()["id"]

        update_payload = {
            "title": "Projet Mis à Jour",
            "description": "Description mise à jour",
            "status": "completed"
        }
        update_response = self.client.put(f"/api/projects/{project_id}", json=update_payload)
        self.assertEqual(update_response.status_code, 200)
        data = update_response.get_json()
        self.assertEqual(data["title"], update_payload["title"])
        self.assertEqual(data["description"], update_payload["description"])
        self.assertEqual(data["status"], update_payload["status"])

    def test_delete_project_success(self):
        payload = {
            "title": "Projet à supprimer",
            "description": "Ce projet va être supprimé"
        }
        create_response = self.client.post("/api/projects", json=payload)
        project_id = create_response.get_json()["id"]

        delete_response = self.client.delete(f"/api/projects/{project_id}")
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn("Project deleted successfully", delete_response.get_data(as_text=True))

        get_response = self.client.get(f"/api/projects/{project_id}")
        self.assertEqual(get_response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
