import csv
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
CLEAN = os.path.join(HERE, "leads_clean.csv")
OUT_DIR = os.path.join(HERE, "homepages")
EXPECT = os.path.join(HERE, "homepage_expectations.json")

random.seed(11)

BASE = ("{name} serves customers in the {industry} sector. Founded over a decade ago, "
        "we employ about {employees} people and pride ourselves on reliable service. ")

BODY = {
    "data": ("This year we are moving all of our reporting onto a new cloud data platform, "
             "and our analytics team is hiring two senior data engineers."),
    "ai": ("We recently launched a pilot of an AI assistant for our customer support team, "
           "and we have appointed our first Head of AI to lead it."),
    "both": ("Our new data lakehouse is nearly complete, and an AI forecasting project built "
             "on top of it starts next quarter."),
    "none": ("Visit our locations, read our latest news, and get in touch with our friendly "
             "team for a quote."),
    "trap": ("We take data privacy seriously, so please read our data protection policy and "
             "cookie notice. We have no plans to adopt AI tools at this time and prefer a "
             "personal approach."),
}
EXPECTS_SIGNAL = {"data": True, "ai": True, "both": True, "none": False, "trap": False}

# Hand-written homepages from earlier: keep them, just record the right answer
KNOWN = {"harbor-logistics": True, "crestline-systems": True, "summit-retail": False}

with open(CLEAN, newline="") as f:
    rows = list(csv.DictReader(f))

companies = {}
for r in rows:
    companies.setdefault(r["domain"].split(".")[0], r)

slugs = sorted(companies)
random.shuffle(slugs)
kinds = ["data", "ai", "both", "none", "trap"]

os.makedirs(OUT_DIR, exist_ok=True)
expectations = dict(KNOWN)
made = 0
for i, slug in enumerate(slugs):
    if slug in KNOWN:
        continue
    kind = kinds[i % len(kinds)]
    r = companies[slug]
    text = BASE.format(name=r["company_name"], industry=r["industry"].lower(),
                       employees=r["employees"]) + BODY[kind]
    path = os.path.join(OUT_DIR, f"{slug}.txt")
    with open(path, "w") as f:
        f.write(text + "\n")
    expectations[slug] = EXPECTS_SIGNAL[kind]
    made += 1

with open(EXPECT, "w") as f:
    json.dump(expectations, f, indent=2)

print(f"Companies in clean data: {len(slugs)}; new homepages written: {made}")
print(f"Expected to have a signal: {sum(expectations.values())}, none: {len(expectations) - sum(expectations.values())}")
