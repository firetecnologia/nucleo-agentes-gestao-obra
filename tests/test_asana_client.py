import unittest

from src.config import AppConfig
from src.integrations.asana_client import AsanaClient


class AsanaClientTests(unittest.TestCase):
    def test_from_config_uses_environment_settings_without_enabling_real_calls(self) -> None:
        config = AppConfig(
            dry_run=True,
            asana_access_token="token-falso",
            asana_workspace_gid="workspace-1",
            asana_project_gid="project-1",
            asana_enable_real_actions=False,
        )

        client = AsanaClient.from_config(config)

        self.assertTrue(client.dry_run)
        self.assertEqual(client.token, "token-falso")
        self.assertEqual(client.workspace_gid, "workspace-1")
        self.assertEqual(client.project_gid, "project-1")
        self.assertFalse(client.enable_real_actions)
        self.assertFalse(client.confirm_real_action)

    def test_fetch_task_is_planned_in_dry_run(self) -> None:
        client = AsanaClient(dry_run=True)

        result = client.fetch_task("task-123")

        self.assertEqual(result["operation"], "fetch_task")
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["task_id"], "task-123")

    def test_post_comment_is_planned_in_dry_run(self) -> None:
        client = AsanaClient(dry_run=True)

        result = client.post_comment("task-123", "Comentário interno de teste.")

        self.assertEqual(result["operation"], "post_comment")
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["task_id"], "task-123")
        self.assertEqual(result["comment"], "Comentário interno de teste.")

    def test_create_task_is_planned_in_dry_run_with_default_project(self) -> None:
        client = AsanaClient(dry_run=True, project_gid="project-1")

        result = client.create_task(
            name="Próxima etapa",
            notes="Tarefa planejada pelo agente.",
        )

        self.assertEqual(result["operation"], "create_task")
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["project_id"], "project-1")
        self.assertEqual(result["name"], "Próxima etapa")

    def test_update_fields_is_planned_in_dry_run(self) -> None:
        client = AsanaClient(dry_run=True)

        result = client.update_fields("task-123", {"status_agente": "Em revisão"})

        self.assertEqual(result["operation"], "update_fields")
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["fields"], {"status_agente": "Em revisão"})

    def test_real_call_is_blocked_without_enable_flag(self) -> None:
        client = AsanaClient(
            dry_run=False,
            token="token-falso",
            enable_real_actions=False,
            confirm_real_action=True,
        )

        with self.assertRaisesRegex(RuntimeError, "ASANA_ENABLE_REAL_ACTIONS"):
            client.post_comment("task-123", "Não enviar.")

    def test_real_call_is_blocked_without_token(self) -> None:
        client = AsanaClient(
            dry_run=False,
            token=None,
            enable_real_actions=True,
            confirm_real_action=True,
        )

        with self.assertRaisesRegex(RuntimeError, "ASANA_ACCESS_TOKEN"):
            client.create_task("Não criar", "Sem token.")

    def test_real_call_is_blocked_without_explicit_confirmation(self) -> None:
        client = AsanaClient(
            dry_run=False,
            token="token-falso",
            enable_real_actions=True,
            confirm_real_action=False,
        )

        with self.assertRaisesRegex(RuntimeError, "confirmação explícita"):
            client.update_fields("task-123", {"campo": "valor"})

    def test_all_real_call_gates_still_stop_at_safe_stub(self) -> None:
        client = AsanaClient(
            dry_run=False,
            token="token-falso",
            enable_real_actions=True,
            confirm_real_action=True,
        )

        with self.assertRaisesRegex(NotImplementedError, "stub seguro"):
            client.fetch_task("task-123")


if __name__ == "__main__":
    unittest.main()
