import unittest

from src.config import AppConfig, parse_bool


class ConfigTests(unittest.TestCase):
    def test_defaults_are_safe(self) -> None:
        config = AppConfig.from_env({})

        self.assertTrue(config.dry_run)
        self.assertIsNone(config.asana_access_token)
        self.assertIsNone(config.asana_workspace_gid)
        self.assertIsNone(config.asana_project_gid)
        self.assertFalse(config.asana_enable_real_actions)

    def test_from_env_reads_asana_settings(self) -> None:
        config = AppConfig.from_env(
            {
                "DRY_RUN": "false",
                "ASANA_ACCESS_TOKEN": "token-falso",
                "ASANA_WORKSPACE_GID": "workspace-1",
                "ASANA_PROJECT_GID": "project-1",
                "ASANA_ENABLE_REAL_ACTIONS": "true",
            }
        )

        self.assertFalse(config.dry_run)
        self.assertEqual(config.asana_access_token, "token-falso")
        self.assertEqual(config.asana_workspace_gid, "workspace-1")
        self.assertEqual(config.asana_project_gid, "project-1")
        self.assertTrue(config.asana_enable_real_actions)

    def test_parse_bool_accepts_portuguese_values(self) -> None:
        self.assertTrue(parse_bool("sim"))
        self.assertFalse(parse_bool("não", default=True))
        self.assertFalse(parse_bool("nao", default=True))

    def test_empty_strings_become_none(self) -> None:
        config = AppConfig.from_env(
            {
                "ASANA_ACCESS_TOKEN": " ",
                "ASANA_WORKSPACE_GID": "",
                "ASANA_PROJECT_GID": "project-1",
            }
        )

        self.assertIsNone(config.asana_access_token)
        self.assertIsNone(config.asana_workspace_gid)
        self.assertEqual(config.asana_project_gid, "project-1")


if __name__ == "__main__":
    unittest.main()
