import csv
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, "leads_raw.csv")
OUT = os.path.join(HERE, "lead_pool.csv")

random.seed(2026)

PRE = ["Alder", "Beacon", "Cobalt", "Dunmore", "Elmstead", "Fairview", "Granite", "Hollis",
       "Juniper", "Kestrel", "Linden", "Meridian", "Oakfield", "Pinecrest", "Quarry",
       "Ridgeway", "Silverline", "Tamarack", "Union", "Vantage"]
SUF = ["Financial", "Logistics", "Health", "Systems", "Retail", "Energy",
       "Insurance", "Manufacturing", "Analytics", "Holdings", "Media", "Foods"]
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
MANAGER_TITLES = ["Senior Manager of Data", "Manager of Business Intelligence",
                  "Manager of Analytics", "Senior Manager of Analytics",
                  "Manager of Data Engineering", "Manager of AI", "Engineering Manager"]
SIGNALS = ["Hiring data engineers", "Announced AI initiative", "Raised funding",
           "New CTO appointed", "Migrating data warehouse", "No recent signal"]
FIELDS = ["company_name", "domain", "industry", "employees", "country", "contact_name", "title",
          "email", "linkedin_url", "intent_signal", "days_in_role", "days_since_linkedin_activity"]

if not os.path.exists(SEED):
    raise SystemExit("leads_raw.csv not found. Run: python3 sample-data/generate_dummy_data.py")
with open(SEED, newline="") as f:
    seed_rows = list(csv.DictReader(f))

combos = [(p, s) for p in PRE for s in SUF]
random.shuffle(combos)

new_rows = []
for p, s in combos[:140]:
    company = f"{p} {s}"
    domain = f"{p.lower()}-{s.lower()}.example"
    employees = random.randint(30, 2000) if random.random() < 0.8 else random.choice([8, 15, 5000, 12000])
    country = random.choices(COUNTRIES, COUNTRY_WEIGHTS)[0]
    industry = random.choice(INDUSTRIES)
    signal = random.choice(SIGNALS)
    for _ in range(random.randint(1, 4)):
        group = random.choices(["data", "ai", "engineering", "other"], [35, 20, 30, 15])[0]
        title = random.choice(TITLES[group])
        if group != "other" and random.random() < 0.3:
            title = random.choice(MANAGER_TITLES)
        first, last = random.choice(FIRST), random.choice(LAST)
        n = len(new_rows)
        new_rows.append({
            "company_name": company, "domain": domain, "industry": industry,
            "employees": employees, "country": country,
            "contact_name": f"{first} {last}", "title": title,
            "email": f"{first}.{last}.{n}@{domain}".lower(),
            "linkedin_url": f"https://www.linkedin.com/in/fake-{first}-{last}-{n}".lower(),
            "intent_signal": signal,
            "days_in_role": random.randint(10, 89) if random.random() < 0.25 else random.randint(90, 2500),
            "days_since_linkedin_activity": random.randint(1, 59) if random.random() < 0.35 else random.randint(60, 400),
        })

for r in random.sample(new_rows, 8):
    r["title"] = ""
for r in random.sample(new_rows, 8):
    r["employees"] = ""

pool = seed_rows + new_rows
with open(OUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(pool)
print(f"Pool: {len(seed_rows)} existing leads + {len(new_rows)} new = {len(pool)} total")
