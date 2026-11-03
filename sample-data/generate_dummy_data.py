import csv, os, random

random.seed(42)  # same data every run

PRE = ["Northwind", "Bluepeak", "Ironbridge", "Summit", "Harbor", "Crestline", "Redwood", "Lakeshore"]
SUF = ["Financial", "Logistics", "Health", "Systems", "Retail", "Energy"]
INDUSTRIES = ["Financial Services", "Insurance", "Health Care", "Manufacturing",
              "Logistics and Supply Chain", "E-commerce", "SaaS and Tech", "Legal",
              "Energy and Utilities", "Automotive", "Telecom", "Government", "Gambling"]
COUNTRIES = ["United States", "Canada", "India", "Germany"]
COUNTRY_WEIGHTS = [60, 15, 15, 10]
FIRST = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery", "Quinn", "Drew"]
LAST = ["Smith", "Nguyen", "Patel", "Garcia", "Brown", "Kim", "Lopez", "Davis", "Clark", "Reed"]
TITLES = {
    "data": ["Head of Data", "VP of Analytics", "Director of Data Engineering", "Head of Business Intelligence"],
    "ai": ["Head of AI", "Director of AI Transformation", "Chief Digital Officer", "Head of Automation"],
    "engineering": ["CTO", "VP of Engineering", "Head of Engineering", "Chief Information Officer"],
    "other": ["Marketing Manager", "HR Business Partner", "Office Manager", "Account Executive"],
}
SIGNALS = ["Hiring data engineers", "Announced AI initiative", "Raised funding",
           "New CTO appointed", "Migrating data warehouse", "No recent signal"]

pairs = [(p, s) for p in PRE for s in SUF]
random.shuffle(pairs)

rows = []
for p, s in pairs[:40]:
    company = f"{p} {s}"
    domain = f"{p.lower()}-{s.lower()}.example"
    employees = random.randint(30, 2000) if random.random() < 0.8 else random.choice([8, 15, 5000, 12000])
    country = random.choices(COUNTRIES, COUNTRY_WEIGHTS)[0]
    industry = random.choice(INDUSTRIES)
    signal = random.choice(SIGNALS)
    for _ in range(random.randint(1, 2)):
        group = random.choices(["data", "ai", "engineering", "other"], [35, 20, 30, 15])[0]
        first, last = random.choice(FIRST), random.choice(LAST)
        rows.append({
            "company_name": company,
            "domain": domain,
            "industry": industry,
            "employees": employees,
            "country": country,
            "contact_name": f"{first} {last}",
            "title": random.choice(TITLES[group]),
            "email": f"{first}.{last}@{domain}".lower(),
            "linkedin_url": f"https://www.linkedin.com/in/fake-{first}-{last}-{random.randint(100, 999)}".lower(),
            "intent_signal": signal,
        })

# Deliberate mess for the cleaning step
for r in random.sample(rows, 3):
    dup = dict(r)
    dup["email"] = dup["email"].upper()
    rows.append(dup)
for r in random.sample(rows, 2):
    r["title"] = ""
for r in random.sample(rows, 2):
    r["employees"] = ""

out = os.path.join(os.path.dirname(__file__), "leads_raw.csv")
with open(out, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {len(rows)} rows to {out}")
