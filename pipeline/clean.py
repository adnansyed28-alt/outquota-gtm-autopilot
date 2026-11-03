import csv
import os
from collections import Counter

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICP_PATH = os.path.join(ROOT, "scoring", "icp.yaml")
RAW_PATH = os.path.join(ROOT, "sample-data", "leads_raw.csv")
CLEAN_PATH = os.path.join(ROOT, "sample-data", "leads_clean.csv")
REJECT_PATH = os.path.join(ROOT, "sample-data", "leads_rejected.csv")


def load_icp():
    with open(ICP_PATH) as f:
        return yaml.safe_load(f)


def build_title_map(icp):
    """Map each target title (lowercase) to (persona group, title tier)."""
    mapping = {}
    for tier, key in (("B", "secondary_personas"), ("A", "personas")):
        for group, titles in icp.get(key, {}).items():
            for t in titles:
                mapping[t.lower()] = (group, tier)
    return mapping


def normalize(row):
    """Strip whitespace, lowercase emails, tidy names."""
    row = {k: (v or "").strip() for k, v in row.items()}
    row["email"] = row["email"].lower()
    row["contact_name"] = row["contact_name"].title()
    return row


def reject_reason(row, icp, title_map):
    """Return why a row is rejected, or None if it passes."""
    # Data quality checks first
    if not row["title"]:
        return "missing title"
    try:
        employees = int(row["employees"])
    except ValueError:
        return "missing employees"

    # ICP checks
    company = icp["company"]
    industries = [i.lower() for i in company["industries"]]
    geographies = [g.lower() for g in company["geographies"]]
    if row["industry"].lower() not in industries:
        return "industry outside ICP"
    if row["country"].lower() not in geographies:
        return "geography outside ICP"
    low, high = company["employee_range"]["min"], company["employee_range"]["max"]
    if employees < low or employees > high:
        return "company size outside ICP"
    if row["title"].lower() not in title_map:
        return "title not in target personas"
    return None


def main():
    icp = load_icp()
    title_map = build_title_map(icp)

    with open(RAW_PATH, newline="") as f:
        raw_rows = list(csv.DictReader(f))

    kept, rejected = [], []
    seen_emails = set()

    for raw in raw_rows:
        row = normalize(raw)

        if row["email"] in seen_emails:
            row["reject_reason"] = "duplicate"
            rejected.append(row)
            continue
        seen_emails.add(row["email"])

        reason = reject_reason(row, icp, title_map)
        if reason:
            row["reject_reason"] = reason
            rejected.append(row)
        else:
            group, tier = title_map[row["title"].lower()]
            row["persona_group"] = group
            row["title_tier"] = tier
            kept.append(row)

    base_fields = list(raw_rows[0].keys())
    with open(CLEAN_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=base_fields + ["persona_group", "title_tier"])
        writer.writeheader()
        writer.writerows(kept)
    with open(REJECT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=base_fields + ["reject_reason"])
        writer.writeheader()
        writer.writerows(rejected)

    print(f"Input rows:    {len(raw_rows)}")
    print(f"Kept:          {len(kept)}")
    print(f"Rejected:      {len(rejected)}")
    for reason, count in Counter(r["reject_reason"] for r in rejected).most_common():
        print(f"  - {reason}: {count}")
    print(f"Persona mix:   {dict(Counter(r['persona_group'] for r in kept))}")


if __name__ == "__main__":
    main()
