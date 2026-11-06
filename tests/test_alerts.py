import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))

import alerts  # noqa: E402


def row(name, tier, level, score):
    return {"contact_name": name, "title": "Head of Data", "company_name": "Acme",
            "tier": tier, "intent_level": level, "total_score": score}


class TestAlerts(unittest.TestCase):
    def test_both_tiers_are_included_when_high_intent(self):
        rows = [row("Ann", "A", "High", "70"), row("Ben", "B", "High", "60")]
        self.assertEqual(alerts.build_message(rows, "2026-11-07")[0], 2)

    def test_standard_intent_is_excluded(self):
        rows = [row("Ann", "A", "Standard", "90"), row("Ben", "B", "High", "60")]
        count, text = alerts.build_message(rows, "2026-11-07")
        self.assertEqual(count, 1)
        self.assertNotIn("Ann", text)

    def test_tier_a_is_listed_before_tier_b(self):
        rows = [row("Ben", "B", "High", "95"), row("Ann", "A", "High", "50")]
        text = alerts.build_message(rows, "2026-11-07")[1]
        self.assertLess(text.index("Ann"), text.index("Ben"))

    def test_higher_score_first_within_a_tier(self):
        rows = [row("Low", "A", "High", "50"), row("Top", "A", "High", "90")]
        text = alerts.build_message(rows, "2026-11-07")[1]
        self.assertLess(text.index("Top"), text.index("Low"))

    def test_empty_day_sends_a_short_message(self):
        count, text = alerts.build_message([row("Ann", "A", "Standard", "80")], "2026-11-07")
        self.assertEqual(count, 0)
        self.assertIn("No High intent leads today", text)

    def test_message_shows_only_name_title_and_company(self):
        text = alerts.build_message([row("Ann", "A", "High", "76.0")], "2026-11-07")[1]
        self.assertIn("Ann, Head of Data, Acme", text)
        self.assertNotIn("76.0", text)


if __name__ == "__main__":
    unittest.main()
