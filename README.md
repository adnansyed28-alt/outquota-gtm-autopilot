# OutQuota: Automated Prospect List Building

An SDR spends hours every week building prospect lists by hand: applying the ICP, qualifying companies, finding the right people, and deciding who to contact first. This project automates that workflow end to end and explains every decision it makes.

Live explainer (planned full system): https://gtm-workflow.vercel.app

> **Status:** the pipeline in this repo is built and runs. It currently works on **synthetic data** (fake companies and people on `.example` domains). The explainer site describes a larger planned system; the roadmap below shows what is built and what is not.

## What it does

1. **Clean:** dedupe, normalize, and drop rows with missing data or outside the ICP (industry, geography, company size). Every rejected row is kept with its reason.
2. **Tier by title:** Tier A = decision-maker titles (Head/Director/VP of Data, AI, Engineering). Tier B = manager-level titles (e.g. Manager of Business Intelligence).
3. **Score:** a fit score (company size, geography, seniority) and an intent score (company triggers plus person-level signals), each with a one-line "why".
4. **Label intent:** a lead is High intent if the person started the role in the last 90 days or was active on LinkedIn in the last 60 days.
5. **Prioritize:** Tier A before Tier B, High intent first within each tier, then by score.
6. **Report:** a funnel summary and the top 10 leads (see `docs/run_summary.md`).

All rules live in config files (`scoring/icp.yaml`, `scoring/scoring_rules.yaml`), so changing the ICP or the weights does not require changing code.

## Results (synthetic data)

| Stage | Leads |
|---|---|
| Raw leads | 64 |
| Rejected (with reasons) | 43 |
| Qualified and scored | 21 |

Segments: A / High 7, A / Standard 7, B / High 2, B / Standard 5. The segment mix reflects how the dummy data was generated, not a real market.

Time saved on real list building has not been measured yet.

## Repo structure

- `scoring/`: ICP and scoring rules (YAML)
- `pipeline/`: `clean.py`, `score.py`, `report.py`, `run_all.py`
- `sample-data/`: synthetic data generator and its outputs
- `docs/`: generated run summary
- `workflows/`, `prompts/`: reserved for the n8n workflow and LLM prompts (roadmap)

## Run it

    pip install -r requirements.txt
    python3 pipeline/run_all.py

## Roadmap

- [ ] LLM company research from a homepage (needs an API key)
- [ ] n8n workflow to schedule the run and send Slack alerts for A / High leads
- [ ] Swap the synthetic data for a real source via an approved data provider
- [ ] Smarter title matching for messy real-world titles

## Data and privacy

No real prospect data is stored in this repo, and no scraping is performed.
