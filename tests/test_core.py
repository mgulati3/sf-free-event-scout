from datetime import datetime, timezone
from event_scout.core import validate_event, ingest, connect_db

BASE = dict(id="evt-a", title="AI Developer Meetup", url="https://luma.com/example",
            city="San Francisco", in_person=True, start_at="2027-01-10T18:00:00-08:00",
            description="Meet engineers", requires_purchase=False, mandatory_fees=0,
            ticket_types=[{"price":0, "currency":"USD", "available":True}])
NOW = datetime(2026, 10, 26, tzinfo=timezone.utc)

def test_free_event_accepted():
    event, reason = validate_event(BASE, NOW)
    assert reason is None and "networking" in event["categories"]

def test_unknown_fees_rejected():
    item = {**BASE, "mandatory_fees":None}
    assert validate_event(item, NOW)[0] is None

def test_unknown_ticket_price_rejected():
    item = {**BASE, "ticket_types":[]}
    assert validate_event(item, NOW)[0] is None

def test_non_bay_area_rejected():
    item = {**BASE, "city":"Los Angeles"}
    assert validate_event(item, NOW)[0] is None

def test_deduplication(tmp_path):
    conn = connect_db(tmp_path / "test.db")
    first = ingest([BASE], conn, NOW)
    second = ingest([BASE], conn, NOW)
    assert len(first["new"]) == 1
    assert not second["new"] and second["updated"] == 1
    assert conn.execute("SELECT count(*) FROM events").fetchone()[0] == 1
    conn.close()
