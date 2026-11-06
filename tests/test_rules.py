import os
import sys
import unittest

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))

import clean  # noqa: E402
import score  # noqa: E402

ICP = yaml.safe_load(open(os.path.join(ROOT, "scoring", "icp.yaml")))
RULES = yaml.safe_load(open(os.path.join(ROOT, "scoring", "scoring_rules.yaml")))
TITLE_MAP = clean.build_title_map(ICP)


def lead(**overrides):
    """A valid, average lead. Tests change one field at a time."""
    base = dict(
        company_name="Test Co", domain="test-co.example", industry="SaaS and Tech",
        employees="300", country="United States", contact_name="Pat Doe",
        title="Head of Data", email="pat@test-co.example", linkedin_url="",
        intent_signal="No recent signal", days_in_role="500",
        days_since_linkedin_activity="200",
    )
    base.update(overrides)
    return base


class TestCleaning(unittest.TestCase):
    def test_valid_lead_passes(self):
        self.assertIsNone(clean.reject_reason(lead(), ICP, TITLE_MAP))

    def test_exact_target_title_is_tier_a(self):
        self.assertEqual(TITLE_MAP["head of data"], ("data", "A"))

    def test_manager_title_is_tier_b(self):
        self.assertEqual(TITLE_MAP["manager of business intelligence"][1], "B")

    def test_unknown_title_is_rejected(self):
        self.assertEqual(clean.reject_reason(lead(title="Marketing Manager"), ICP, TITLE_MAP),
                         "title not in target personas")

    def test_geography_outside_icp(self):
        self.assertEqual(clean.reject_reason(lead(country="India"), ICP, TITLE_MAP),
                         "geography outside ICP")

    def test_company_too_small(self):
        self.assertEqual(clean.reject_reason(lead(employees="8"), ICP, TITLE_MAP),
                         "company size outside ICP")

    def test_company_too_large(self):
        self.assertEqual(clean.reject_reason(lead(employees="5000"), ICP, TITLE_MAP),
                         "company size outside ICP")

    def test_industry_outside_icp(self):
        self.assertEqual(clean.reject_reason(lead(industry="Gambling"), ICP, TITLE_MAP),
                         "industry outside ICP")

    def test_missing_title_and_employees(self):
        self.assertEqual(clean.reject_reason(lead(title=""), ICP, TITLE_MAP), "missing title")
        self.assertEqual(clean.reject_reason(lead(employees=""), ICP, TITLE_MAP), "missing employees")

    def test_email_is_normalized(self):
        self.assertEqual(clean.normalize(lead(email="  PAT@Test-Co.EXAMPLE "))["email"],
                         "pat@test-co.example")


class TestScoring(unittest.TestCase):
    def test_new_hire_is_high_intent(self):
        self.assertTrue(score.is_high_intent(lead(days_in_role="30"), RULES))

    def test_recent_linkedin_activity_is_high_intent(self):
        self.assertTrue(score.is_high_intent(lead(days_since_linkedin_activity="20"), RULES))

    def test_neither_signal_is_standard(self):
        self.assertFalse(score.is_high_intent(lead(), RULES))

    def test_boundaries(self):
        self.assertTrue(score.is_high_intent(lead(days_in_role="90"), RULES))
        self.assertFalse(score.is_high_intent(lead(days_in_role="91"), RULES))
        self.assertTrue(score.is_high_intent(lead(days_since_linkedin_activity="60"), RULES))
        self.assertFalse(score.is_high_intent(lead(days_since_linkedin_activity="61"), RULES))

    def test_missing_signal_data_is_not_high_intent(self):
        row = lead(days_in_role="", days_since_linkedin_activity="")
        self.assertFalse(score.is_high_intent(row, RULES))

    def test_intent_score_is_capped_at_100(self):
        row = lead(intent_signal="Migrating data warehouse", days_in_role="10",
                   days_since_linkedin_activity="5")
        self.assertEqual(score.score_intent(row, RULES)[0], 100)

    def test_strong_signal_beats_no_signal(self):
        strong = score.score_intent(lead(intent_signal="Announced AI initiative"), RULES)[0]
        none = score.score_intent(lead(intent_signal="No recent signal"), RULES)[0]
        self.assertGreater(strong, none)

    def test_senior_title_outscores_manager_title(self):
        fit = RULES["fit"]
        self.assertGreater(score.seniority_points("CTO", fit)[0],
                           score.seniority_points("Manager of Analytics", fit)[0])

    def test_us_outscores_canada(self):
        us = score.score_fit(lead(country="United States"), RULES)[0]
        ca = score.score_fit(lead(country="Canada"), RULES)[0]
        self.assertGreater(us, ca)

    def test_sweet_spot_size_beats_edge_of_range(self):
        sweet = score.score_fit(lead(employees="300"), RULES)[0]
        edge = score.score_fit(lead(employees="1900"), RULES)[0]
        self.assertGreater(sweet, edge)


if __name__ == "__main__":
    unittest.main()
