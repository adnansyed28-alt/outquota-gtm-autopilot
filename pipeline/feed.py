import argparse
import csv
import datetime
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
POOL = os.path.join(ROOT, "sample-data", "lead_pool.csv")
BATCH = os.path.join(ROOT, "sample-data", "leads_batch.csv")
STATE_DIR = os.path.join(ROOT, "state")
SEEN = os.path.join(STATE_DIR, "seen_leads.csv")
DAILY_LIMIT = 40


def norm_email(row):
    return row.get("email", "").strip().lower()


def release(rows, seen, limit):
    """Return the next `limit` rows whose email was not released on an earlier run."""
    batch = []
    for row in rows:
        if norm_email(row) in seen:
            continue
        batch.append(row)
        if len(batch) >= limit:
            break
    return batch


def load_seen():
    if not os.path.exists(SEEN):
        return set()
    with open(SEEN, newline="") as f:
        return {r["email"] for r in csv.DictReader(f)}


def remember(batch):
    os.makedirs(STATE_DIR, exist_ok=True)
    is_new = not os.path.exists(SEEN)
    today = datetime.date.today().isoformat()
    with open(SEEN, "a", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["email", "released_on"])
        for row in batch:
            writer.writerow([norm_email(row), today])


def main():
    parser = argparse.ArgumentParser(description="Release the next batch of unseen leads.")
    parser.add_argument("--limit", type=int, default=DAILY_LIMIT)
    parser.add_argument("--reset", action="store_true", help="forget all released leads")
    args = parser.parse_args()

    if args.reset and os.path.exists(SEEN):
        os.remove(SEEN)
        print("Cleared the list of released leads.")
    if not os.path.exists(POOL):
        raise SystemExit("Lead pool not found. Run: python3 sample-data/generate_lead_pool.py")

    with open(POOL, newline="") as f:
        rows = list(csv.DictReader(f))

    seen = load_seen()
    batch = release(rows, seen, args.limit)
    if not batch:
        raise SystemExit("The lead pool is used up. Run with --reset to start again.")

    with open(BATCH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(batch)
    remember(batch)

    seen_after = seen | {norm_email(r) for r in batch}
    remaining = sum(1 for r in rows if norm_email(r) not in seen_after)
    print(f"Released {len(batch)} new leads. Left in the pool: {remaining}")


if __name__ == "__main__":
    main()
