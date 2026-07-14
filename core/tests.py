import json

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import Task, Frequency, AuditLog


class CoreApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="adminpass", is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username="usuario", email="usuario@example.com", password="userpass"
        )
        self.task = Task.objects.create(title="Tarefa inicial", description="Descrição de teste")
        self.frequency = Frequency.objects.create(user=self.normal_user, method="manual", present=True)
        settings.SUAP_API_KEY = "test-api-key"

    def test_task_endpoints_can_create_and_move(self):
        response = self.client.post(
            "/api/tasks/",
            data=json.dumps({"title": "Nova tarefa", "description": "Teste"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("task", payload)
        self.assertEqual(payload["task"]["title"], "Nova tarefa")

        task_id = payload["task"]["id"]
        response = self.client.post(
            f"/api/tasks/{task_id}/move/",
            data=json.dumps({"status": "done"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["task"]["status"], "done")

    def test_suap_sync_requires_authorization_and_logs_api_key(self):
        response = self.client.post(
            "/api/suap-sync/",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(AuditLog.objects.filter(auth_type="unauthorized").count(), 1)

        response = self.client.post(
            "/api/suap-sync/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_X_API_KEY="test-api-key",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("results", payload)
        self.assertTrue(payload["results"][0]["ok"])
        self.assertEqual(AuditLog.objects.filter(auth_type="api_key").count(), 1)

    def test_dashboard_and_orientador_endpoints_return_data(self):
        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("tasks", payload)
        self.assertIn("frequencies", payload)
        self.assertEqual(payload["frequencies"]["total"], 1)

        response = self.client.get("/api/orientador-summary/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("students", payload)
        self.assertTrue(len(payload["students"]) >= 1)

    def test_audit_logs_protected_by_staff(self):
        response = self.client.get("/api/audit-logs/")
        self.assertEqual(response.status_code, 401)

        self.client.login(username="admin", password="adminpass")
        response = self.client.get("/api/audit-logs/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("logs", payload)
