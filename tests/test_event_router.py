import unittest

from src.events.event_router import UnknownEventTypeError, route_event


class EventRouterTests(unittest.TestCase):
    def test_route_known_event(self) -> None:
        route = route_event("task_ready_for_agent_review")

        self.assertEqual(route.event_type, "task_ready_for_agent_review")
        self.assertEqual(route.handler_name, "_handle_task_ready_for_agent_review")

    def test_unknown_event_raises_controlled_error(self) -> None:
        with self.assertRaisesRegex(UnknownEventTypeError, "Tipo de evento desconhecido"):
            route_event("evento_inexistente")


if __name__ == "__main__":
    unittest.main()
