import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))

import feed  # noqa: E402


def rows(*emails):
    return [{"email": e, "company_name": "X"} for e in emails]


class TestFeed(unittest.TestCase):
    def test_respects_the_daily_limit(self):
        self.assertEqual(len(feed.release(rows("a@x", "b@x", "c@x"), set(), 2)), 2)

    def test_skips_leads_released_on_earlier_runs(self):
        batch = feed.release(rows("a@x", "b@x", "c@x"), {"b@x"}, 10)
        self.assertEqual([r["email"] for r in batch], ["a@x", "c@x"])

    def test_email_match_ignores_case_and_spaces(self):
        self.assertEqual(feed.release(rows("  A@X "), {"a@x"}, 10), [])

    def test_duplicates_inside_one_batch_are_left_for_cleaning(self):
        self.assertEqual(len(feed.release(rows("a@x", "A@X"), set(), 10)), 2)

    def test_nothing_left_when_everything_was_seen(self):
        self.assertEqual(feed.release(rows("a@x", "b@x"), {"a@x", "b@x"}, 10), [])


if __name__ == "__main__":
    unittest.main()
