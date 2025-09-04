from django.test import TestCase
from rest_framework.test import APIClient
from .models import Experiment

class ExperimentAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.exp1 = Experiment.objects.create(title="Test Exp 1", description="demo")

    def test_list_experiments(self):
        response = self.client.get("/api/experiments/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_create_experiment(self):
        response = self.client.post("/api/experiments/", {"title": "Exp 2", "description": "desc"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "Exp 2")

    def test_retrieve_experiment(self):
        response = self.client.get(f"/api/experiments/{self.exp1.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Test Exp 1")
