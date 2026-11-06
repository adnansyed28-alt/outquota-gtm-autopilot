import unittest

from test_rules import RULES, lead
import score


class TestResearchJoin(unittest.TestCase):
    def test_researched_signals_drive_intent(self):
        row = lead(days_in_role="500", days_since_linkedin_activity="500")
        row["_research"] = {"data_ai_signals": ["a", "b"]}
        points, why = score.score_intent(row, RULES)
        self.assertEqual(points, 50)
        self.assertIn("researched", why)

    def test_researched_points_are_capped(self):
        row = lead(days_in_role="500", days_since_linkedin_activity="500")
        row["_research"] = {"data_ai_signals": ["a", "b", "c", "d", "e"]}
        self.assertEqual(score.score_intent(row, RULES)[0], 70)

    def test_no_signals_found_scores_only_the_default(self):
        row = lead(intent_signal="Migrating data warehouse",
                   days_in_role="500", days_since_linkedin_activity="500")
        row["_research"] = {"data_ai_signals": []}
        self.assertEqual(score.score_intent(row, RULES)[0], 5)

    def test_failed_research_falls_back_to_dummy_signal(self):
        row = lead(intent_signal="Raised funding",
                   days_in_role="500", days_since_linkedin_activity="500")
        row["_research"] = {"error": "API error 429"}
        points, why = score.score_intent(row, RULES)
        self.assertEqual(points, 45)
        self.assertIn("no research", why)

    def test_missing_research_falls_back_to_dummy_signal(self):
        row = lead(intent_signal="Raised funding",
                   days_in_role="500", days_since_linkedin_activity="500")
        self.assertEqual(score.score_intent(row, RULES)[0], 45)


if __name__ == "__main__":
    unittest.main()
