import unittest

from python_project import greet
from python_project.fund_flow import get_sector_fund_flows
from python_project.t_monitor import get_t_monitor_quote


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

    def test_t_monitor_quote(self) -> None:
        data = get_t_monitor_quote("600519")

        self.assertEqual(data["stock"]["code"], "600519")
        self.assertEqual(data["stock"]["name"], "贵州茅台")
        self.assertEqual(data["initial_price"], 1482.50)
        self.assertGreater(data["current_price"], data["initial_price"])
        self.assertAlmostEqual(data["change_percent"], 5.0, delta=0.11)
        self.assertGreater(data["average_price"], 0)
        self.assertAlmostEqual(data["average_change_percent"], 2.0, delta=0.05)
        self.assertAlmostEqual(
            data["change_percent"],
            round((data["current_price"] / data["initial_price"] - 1) * 100, 2),
        )
        self.assertTrue(data["is_mock"])


if __name__ == "__main__":
    unittest.main()
