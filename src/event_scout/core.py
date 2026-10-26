"""Conservative event normalisation, free-admission verification, and storage."""
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

TARGET_CITIES = {
    "san francisco", "south san francisco", "palo alto", "menlo park",
    "mountain view", "san jose", "redwood city", "sunnyvale",
    "santa clara", "cupertino", "berkeley", "oakland",
}
CATEGORIES = {
    "networking": ("networking", "meetup", "founder", "engineer", "developer", "community"),
    "recruiting": ("recruit", "hiring", "career", "new grad", "early career", "job fair"),
    "hq_visit": ("headquarters", "office tour", "office hours", "open house", "at our office"),
    "linkedin": ("conference", "summit", "demo day", "launch", "hackathon", "ai", "tech talk"),
    "food_popups": ("food", "popup", "pop-up", "tasting", "festival", "supper club"),
}


def _safe_dt(value):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return None
        return dt
    except (TypeError, ValueError, AttributeError):
        return None


def classify(item):
    words = (str(item.get("title", "")) + " " + str(item.get("description", ""))).lower()
    return [name for name, phrases in CATEGORIES.items() if any(p in words for p in phrases)]


def free_evidence(item):
    """Only accept explicit 0-priced entry tickets with no known mandatory charge.

    Unknown price / marketing copy saying 'free' is insufficient.
    This does not confirm that no external fees or required purchases exist.
    """
    if item.get("requires_purchase") is not False:
        return False, "Mandatory-purchase status unverified"
    if item.get("mandatory_fees") != 0:
        return False, "Mandatory fees unknown or non-zero"
    tickets = item.get("ticket_types")
    if not isinstance(tickets, list) or not tickets:
        return False, "No structured ticket-price evidence"
    if not any(t.get("available") is True and isinstance(t.get("price"), (float, int))
               and not isinstance(t.get("price"), bool) and t["price"] == 0
               and t.get("currency") == "USD" for t in tickets if isinstance(t, dict)):
        return False, "No available USD $0 ticket verified"
    if item.get("admission_note") and re.search(r"(minimum spend|required purchase|mandatory fee|cover charge)",
                                                str(item["admission_note"]), re.I):
        return False, "Potential mandatory charge in admission note"
    return True, "Structured USD $0 ticket; mandatory fees reported as zero"


def validate_event(item, now=None):
    now = now or datetime.now(timezone.utc)
    if not isinstance(item, dict):
        return None, "Event is not an object"
    event_id, title, url = item.get("id"), item.get("title"), item.get("url")
    if not all(isinstance(v, str) and v.strip() for v in (event_id, title, url)):
        return None, "Missing id/title/url"
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {"luma.com", "lu.ma", "www.luma.com", "www.lu.ma"}:
        return None, "URL is not a supported HTTPS Luma event page"
    date = _safe_dt(item.get("start_at"))
    if not date or date.astimezone(timezone.utc) <= now:
        return None, "Invalid or past event date"
    city = str(item.get("city", "")).strip().lower()
    if city not in TARGET_CITIES or item.get("in_person") is not True:
        return None, "Outside selected cities or not verified in-person"
    free, reason = free_evidence(item)
    if not free:
        return None, reason
    categories = classify(item)
    if not categories:
        return None, "Not in a chosen event category"
    return {
        "id": event_id, "title": title, "url": url, "city": city.title(),
        "start_at": date.isoformat(), "description": str(item.get("description", "")),
        "categories": categories, "price_evidence": reason,
        "registration_status": "not_registered",
    }, None


def connect_db(db_path):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("""CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL,
        city TEXT NOT NULL, start_at TEXT NOT NULL, description TEXT NOT NULL,
        categories TEXT NOT NULL, price_evidence TEXT NOT NULL,
        registration_status TEXT NOT NULL DEFAULT 'not_registered',
        first_seen_at TEXT NOT NULL, last_seen_at TEXT NOT NULL
    )""")
    conn.commit()
    return conn


def ingest(events, conn, now=None):
    now = now or datetime.now(timezone.utc)
    stamp = now.isoformat()
    outcome = {"new": [], "updated": 0, "rejected": []}
    for raw in events:
        event, reason = validate_event(raw, now=now)
        if reason:
            outcome["rejected"].append({"title": raw.get("title", "<unknown>") if isinstance(raw, dict) else "<unknown>", "reason": reason})
            continue
        exists = conn.execute("SELECT 1 FROM events WHERE id=?", (event["id"],)).fetchone()
        if exists:
            conn.execute("""UPDATE events SET title=?,url=?,city=?,start_at=?,description=?,
                categories=?,price_evidence=?,last_seen_at=? WHERE id=?""",
                (event["title"],event["url"],event["city"],event["start_at"],
                 event["description"],json.dumps(event["categories"]),event["price_evidence"],stamp,event["id"]))
            outcome["updated"] += 1
        else:
            conn.execute("""INSERT INTO events
                (id,title,url,city,start_at,description,categories,price_evidence,registration_status,first_seen_at,last_seen_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (event["id"],event["title"],event["url"],event["city"],event["start_at"],
                 event["description"],json.dumps(event["categories"]),event["price_evidence"],
                 event["registration_status"],stamp,stamp))
            outcome["new"].append(event)
    conn.commit()
    return outcome
