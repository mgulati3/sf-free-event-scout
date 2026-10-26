# SF Free Event Scout

A Python project to discover genuinely free Bay Area events for networking, new-grad recruiting, company HQ visits, LinkedIn content and unusual food pop-ups.

**Status: Phase 1 offline prototype.** This repository currently imports JSON sample events, verifies structured $0 admission with no reported mandatory fees, filters by location and category, deduplicates and stores events in SQLite. Luma live discovery, AI scoring, 3-hour scheduled monitoring, email alerts and registrations are **not active**.

## Start here on macOS

Install Python 3.11+ and Git. Open Terminal and run:

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

The first sample event is accepted. The second is rejected because mandatory costs are unknown. The sample events are **fictional**, not Luma recommendations. Ingest again to see duplicate detection. Data is saved at `data/events.db` and is ignored by Git. Input schema is demonstrated in `data/sample_events.json`.

## Preferences for later phases

See `.env.example`. Settings to implement: verified free events only, minimum AI score **60**, registration mode **approval**, weekly registration limit **3**, interval **3 hours**, notifications **email**. The current app does not read those preferences yet.

## Exploring Luma MCP

See https://help.luma.com/p/mcp. With Claude Code installed, run:

```bash
claude mcp add --transport http luma https://mcp.luma.com
```

Then use `/mcp` in Claude Code and sign in. Search public events by place, date and topic, and inspect pricing fields before implementing a Python source adapter. Don't treat missing pricing or mandatory-fee information as proof that an event is free.

Unattended MCP OAuth authentication in GitHub Actions has **not** been verified. Luma MCP does not document guest registration for third-party events. Never report an RSVP as registered unless confirmation is verified.

## GitHub Actions

The current `.github/workflows/tests.yml` **only runs pytest** on pushes and pull requests. It does not run scheduled discovery or notifications. Later scheduled execution will need persistent cloud state because GitHub runners are ephemeral, plus secure email credentials. Don't commit passwords, OAuth tokens or `.env`.

## Roadmap

1. **Phase 1, now:** Offline validation, categorisation, SQLite, sample data, tests and CI.
2. **Phase 2:** Authenticate to Luma MCP, ingest real public events and score for relevance.
3. **Phase 3:** Persist event history between scheduled runs and send email for new events scoring at least 60, checking every three hours.
4. **Phase 4:** User-approved registration workflow, confirmation verification, max three weekly registration requests.

No automatic registration is implemented.
