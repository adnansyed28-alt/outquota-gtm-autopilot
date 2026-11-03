import csv
import os
import re
from collections import Counter

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICP_PATH = os.path.join(ROOT, "scoring", "icp.yaml")
RULES_PATH = os.path.join(ROOT, "scoring", "scoring_rules.yaml")
CLEAN_PATH = os.path.join(ROOT, "sample-data", "leads_clean.csv")
SCORED_PATH = os.path.join(ROOT, "sample-data", "leads_scored.csv")


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def size_points(employees, fit_rules):
    for band in fit_rules["company_size"]:
        if band["min"] <= employees <= band["max"]:
            return band["points"], f"{employees} employees (sweet spot band)"
    return fit_rules["company_size_default"], f"{employees} employees (edge of range)"


def seniority_points(title, fit_rules):
    for rule in fit_rules["seniority"]:
        if re.search(rf"\b({rule['pattern']})\b", title.lower()):
            return rule["points"], f"{title}"
    return fit_rules["seniority_default"], f"{title} (no seniority match)"


def band_points(days, bands):
    """Return points for the first band whose max_days covers the value."""
    if days is None:
        return 0
    for band in bands:
        if days <= band["max_days"]:
            return band["points"]
    return 0


def score_fit(row, rules):
    fit = rules["fit"]
    size_pts, size_why = size_points(int(row["employees"]), fit)
    geo_pts = fit["geography"].get(row["country"], fit["geography_default"])
    sen_pts, sen_why = seniority_points(row["title"], fit)
    fit_score = size_pts + geo_pts + sen_pts
    why = f"Fit {fit_score}: {size_why}, {row['country']}, {sen_why}"
    return fit_score, why


def score_intent(row, rules):
    intent = rules["intent"]
    parts, notes = [], []

    company_pts = intent["company_signals"].get(row["intent_signal"], intent["company_default"])
    parts.append(company_pts)
    notes.append(f"{row['intent_signal']} (+{company_pts})")

    days_in_role = to_int(row.get("days_in_role"))
    role_pts = band_points(days_in_role, intent["new_in_role"])
    if role_pts:
        parts.append(role_pts)
        notes.append(f"started role {days_in_role} days ago (+{role_pts})")

    days_active = to_int(row.get("days_since_linkedin_activity"))
    act_pts = band_points(days_active, intent["linkedin_activity"])
    if act_pts:
        parts.append(act_pts)
        notes.append(f"active on LinkedIn {days_active} days ago (+{act_pts})")

    intent_score = min(sum(parts), intent["cap"])
    why = f"Intent {intent_score}: " + ", ".join(notes)
    return intent_score, why


def is_high_intent(row, rules):
    """High intent = recently started the role OR recently active on LinkedIn."""
    cfg = rules["high_intent"]
    days_in_role = to_int(row.get("days_in_role"))
    days_active = to_int(row.get("days_since_linkedin_activity"))
    new_hire = days_in_role is not None and days_in_role <= cfg["new_in_role_max_days"]
    active = days_active is not None and days_active <= cfg["linkedin_activity_max_days"]
    return new_hire or active


def tier_for(total, tiers):
    if total >= tiers["A"]:
        return "A"
    if total >= tiers["B"]:
        return "B"
    return "C"


def main():
    icp = load_yaml(ICP_PATH)
    rules = load_yaml(RULES_PATH)
    w_fit, w_intent = icp["weights"]["fit"], icp["weights"]["intent"]

    with open(CLEAN_PATH, newline="") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        fit_score, fit_why = score_fit(row, rules)
        intent_score, intent_why = score_intent(row, rules)
        total = round(fit_score * w_fit + intent_score * w_intent, 1)
        row["fit_score"] = fit_score
        row["intent_score"] = intent_score
        row["total_score"] = total
        row["tier"] = row["title_tier"]
        row["intent_level"] = "High" if is_high_intent(row, rules) else "Standard"
        row["why"] = f"{fit_why}. {intent_why}."

    rows.sort(key=lambda r: (r["tier"], r["intent_level"] != "High", -r["total_score"]))

    with open(SCORED_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Scored {len(rows)} leads")
    print(f"Tier mix: {dict(sorted(Counter(r['tier'] for r in rows).items()))}")
    mix = Counter(f"{r['tier']}/{r['intent_level']}" for r in rows)
    print(f"Tier / intent mix: {dict(sorted(mix.items()))}")
    print("Top 5:")
    for r in rows[:5]:
        print(f"  {r['total_score']:>5}  {r['tier']}/{r['intent_level']}  {r['contact_name']}, {r['title']} @ {r['company_name']}")
        print(f"         {r['why']}")


if __name__ == "__main__":
    main()
