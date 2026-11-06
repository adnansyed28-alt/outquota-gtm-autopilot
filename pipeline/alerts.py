import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCORED = os.path.join(ROOT, "sample-data", "leads_scored.csv")


def main():
    with open(SCORED, newline="") as f:
        rows = list(csv.DictReader(f))
    hot = [r for r in rows if r["tier"] == "A" and r["intent_level"] == "High"]
    hot.sort(key=lambda r: -float(r["total_score"]))
    alerts = [
        {
            "contact": r["contact_name"],
            "title": r["title"],
            "company": r["company_name"],
            "score": float(r["total_score"]),
            "why": r["why"],
            "opener": r["research_hook"],
        }
        for r in hot[:5]
    ]
    print(json.dumps(alerts))


if __name__ == "__main__":
    main()
