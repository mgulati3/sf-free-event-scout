# SF Free Event Scout

Python project to find genuinely free Bay Area events: networking, new-grad hiring, company HQ experiences, LinkedIn-worthy tech events and food pop-ups.

**Current status: Phase 1 (offline).** Imports event JSON, validates confirmed $0 tickets and no mandatory costs, filters locations/categories, and stores results in SQLite without duplicates. **Live Luma MCP, AI scoring, email alerts, scheduled discovery and registration are not yet implemented.** Sample events are fictional.

## Setup (macOS)

Prerequisites: Python 3.11+ and Git.

```bash
git clone https://github.com/mgulati3/sf-free-event-scout.git
cd sf-free-event-scout
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
event-scout ingest --file data/sample_events.json
event-scout list
```

Expected: first fictional sample accepted, second rejected because entry costs are unverified. Run ingest again to check deduplication. SQLite database: `data/events.db` (ignored by Git). View full sample input schema in `data/sample_events.json`.

## Configure future features

Copy `.env.example` to `.env` and leave credentials empty until the next phase. Preferences: only free, verified, in-person Bay Area events, minimum score 60, email only, check every 3 hours, approval before registration, max 3 weekly requests. **These options are not active yet.**

## Luma MCP (manual exploration, not integrated yet)

See [official Luma MCP instructions](https://help.luma.com/p/mcp). To connect Claude Code:

```bash
claude mcp add --transport http luma https://mcp.luma.com
```

Within Claude Code, open `/mcp` and sign in. Search public Bay Area events and inspect which fields are returned. A listing without verified $0 ticket and mandatory-fee information must not be treated as free. Luma's OAuth flow and unattended GitHub Actions authentication have **not** been verified. Luma MCP doesn't document guest RSVP registration for third-party events. Opening an RSVP link is not confirmation.

## GitHub Actions

The current workflow only runs tests on pushes/PRs. It **does not** run scheduled event searches or send emails. GitHub runners are ephemeral, so a later scheduled version requires persistent storage and secure secrets.

## Roadmap

1. Phase 1: Local JSON ingestion, categories, conservative admission filter, SQLite, tests.
2. Phase 2: Verify Luma MCP OAuth, fetch actual events and add AI scoring >=60.
3. Phase 3: Persistent data, scheduled 3-hour checks and email notifications.
4. Phase 4: Approval-based sign-ups, confirmed registration tracking and a weekly limit of three.

Never commit tokens or passwords. No automatic registrations happen in this version.
