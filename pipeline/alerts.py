import csv
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCORED = os.path.join(ROOT, "sample-data", "leads_scored.csv")


def hot_leads(rows):
    """Any High intent lead, Tier A first, then by score."""
    hot = [r for r in rows if r["intent_level"] == "High"]
    hot.sort(key=lambda r: (r["tier"], -float(r["total_score"])))
    return hot


def build_message(rows, today):
    """Return (count, Slack message text): one digest, or a short message on an empty day."""
    hot = hot_leads(rows)
    if not hot:
        return 0, f"No High intent leads today ({today}). The workflow ran and found none."
    lines = [f"{len(hot)} High intent lead(s) for {today}:"]
    for r in hot:
        lines.append(f"- {r['contact_name']}, {r['title']}, {r['company_name']}")
    return len(hot), "\n".join(lines)


def main():
    with open(SCORED, newline="") as f:
        rows = list(csv.DictReader(f))
    count, text = build_message(rows, datetime.date.today().isoformat())
    print(json.dumps({"count": count, "text": text}))


if __name__ == "__main__":
    main()
