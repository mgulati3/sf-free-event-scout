"""Phase 1 CLI: ingest a verified, normalised event JSON feed."""
import argparse
import json
from pathlib import Path
from .core import connect_db, ingest


def main():
    p = argparse.ArgumentParser(description="Free Bay Area event discovery: Phase 1")
    p.add_argument("command", choices=["ingest", "list"])
    p.add_argument("--file", type=Path, help="JSON array of normalised event records")
    p.add_argument("--db", default="data/events.db")
    args = p.parse_args()
    conn = connect_db(args.db)
    try:
        if args.command == "ingest":
            if not args.file:
                p.error("--file is required for ingest")
            payload = json.loads(args.file.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                p.error("The JSON file must contain an array")
            result = ingest(payload, conn)
            print(json.dumps(result, indent=2))
        else:
            for row in conn.execute("SELECT title,city,start_at,url,registration_status FROM events ORDER BY start_at"):
                print(" | ".join(row))
    finally:
        conn.close()

if __name__ == "__main__":
    main()
