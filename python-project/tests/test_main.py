import unittest

from python_project import greet
from python_project.fund_flow import get_sector_fund_flows


class GreetTest(unittest.TestCase):
    def test_greet_default_name(self) -> None:
        self.assertEqual(greet(), "Hello, World!")

    def test_greet_custom_name(self) -> None:
        self.assertEqual(greet("Codex"), "Hello, Codex!")

    def test_sector_fund_flows(self) -> None:
        data = get_sector_fund_flows()

        self.assertIn("summary", data)
        self.assertGreaterEqual(len(data["sectors"]), 2)
        self.assertEqual(data["sectors"][0]["id"], "robotics")
        self.assertIn("net_inflow_text", data["sectors"][0])


if __name__ == "__main__":
    unittest.main()
