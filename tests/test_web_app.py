import unittest

from src.web import create_web_app


class WebAppTests(unittest.TestCase):
    def test_main_pages_return_renderable_html(self) -> None:
        app = create_web_app()
        routes = [
            ("/", "Obra Piloto Nucleo"),
            ("/dashboard", "Dashboard executivo"),
            ("/historico-decisoes", "Historico de decisoes"),
            ("/relatorio-semanal", "Relatorio semanal"),
            ("/rascunho-cliente", "Rascunho para cliente"),
        ]

        for route, expected in routes:
            response = app.get(route)
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/html", response.content_type)
            self.assertIn(expected, response.body)
            self.assertTrue(response.dry_run)
            self.assertEqual(response.external_operations, [])

    def test_client_draft_has_human_review_warning_and_no_external_send(self) -> None:
        response = create_web_app().get("/rascunho-cliente")
        body = response.body.lower()

        self.assertIn("revisao humana obrigatoria", body)
        self.assertIn("draft_only_no_external_send", body)
        self.assertNotIn("send_client_message", body)
        self.assertNotIn("whatsapp", body)
        self.assertNotIn("email", body)

    def test_static_css_is_local(self) -> None:
        response = create_web_app().get("/static/styles.css")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/css", response.content_type)
        self.assertIn(".shell", response.body)

    def test_unknown_route_returns_404_html(self) -> None:
        response = create_web_app().get("/nao-existe")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Rota local nao encontrada", response.body)


if __name__ == "__main__":
    unittest.main()
