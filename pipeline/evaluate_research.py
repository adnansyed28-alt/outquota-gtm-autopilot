import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "sample-data")
EXPECT = os.path.join(DATA, "homepage_expectations.json")
RESEARCH = os.path.join(DATA, "research_output.json")
HOMEPAGES = os.path.join(DATA, "homepages")
OUT = os.path.join(ROOT, "docs", "research_eval.md")


def norm(text):
    return " ".join(text.lower().split())


def main():
    expected = json.load(open(EXPECT))
    research = json.load(open(RESEARCH))

    rows, pending = [], []
    for slug in sorted(expected):
        result = research.get(slug)
        if result is None or "error" in result:
            pending.append(slug)
            continue

        problems = []
        signals = result.get("data_ai_signals") or []
        has_signal = len(signals) > 0
        if has_signal and not expected[slug]:
            problems.append("found a signal that is not in the text")
        if not has_signal and expected[slug]:
            problems.append("missed a real signal")

        quote = result.get("evidence_quote", "")
        if quote:
            text = open(os.path.join(HOMEPAGES, slug + ".txt")).read()
            if norm(quote) not in norm(text):
                problems.append("quote is not in the homepage text")

        if not has_signal and result.get("outreach_hook"):
            problems.append("hook written without a signal")

        rows.append((slug, expected[slug], has_signal, problems))

    passed = sum(1 for r in rows if not r[3])
    lines = ["# Research step evaluation", "",
             "_Checked against hand-written expected answers on synthetic homepages._", "",
             f"**{passed} of {len(rows)} researched companies passed all checks.**"
             + (f" {len(pending)} not researched yet." if pending else ""), "",
             "| Company | Signal expected | Signal found | Result |", "|---|---|---|---|"]
    for slug, exp, found, problems in rows:
        lines.append(f"| {slug} | {'yes' if exp else 'no'} | {'yes' if found else 'no'} | "
                     f"{'pass' if not problems else '; '.join(problems)} |")
    if pending:
        lines += ["", "Not researched yet: " + ", ".join(pending)]
    lines += ["", "Caveat: the pages and the expected answers were both written for this project, "
              "so this shows the checks work, not how the model will do on real company websites."]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write("\n".join(lines) + "\n")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
