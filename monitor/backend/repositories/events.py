from db import connect_db


def create_event(event):
    with connect_db() as conn:
        conn.execute(
            """INSERT INTO http_events
               (method, path, status_code, event_type, attempted_username, source_event_id, occurred_at)
               VALUES (%s, %s, %s, %s, %s, %s, COALESCE(%s, NOW()))
               ON CONFLICT (source_event_id) DO NOTHING""",
            (event["method"], event["path"], event["status_code"],
             event["event_type"], event.get("attempted_username"), event.get("source_event_id"),
             event.get("source_occurred_at")),
        )


def list_events(event_type):
    with connect_db() as conn:
        if event_type is None:
            rows = conn.execute("SELECT * FROM http_events ORDER BY id DESC LIMIT 50").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM http_events WHERE event_type = %s ORDER BY id DESC LIMIT 50",
                (event_type,),
            ).fetchall()
    for row in rows:
        row["occurred_at"] = row["occurred_at"].isoformat()
    return rows


def latest_event_id():
    with connect_db() as conn:
        row = conn.execute("SELECT COALESCE(MAX(id), 0) AS id FROM http_events").fetchone()
    return row["id"]


def events_after(after_id, since, until=None):
    until = until or since
    with connect_db() as conn:
        rows = conn.execute(
            """SELECT id, occurred_at, method, path, status_code, event_type,
                      attempted_username, source_event_id
               FROM http_events WHERE id > %s AND occurred_at >= %s AND occurred_at <= %s
               ORDER BY id ASC""",
            (after_id, since, until),
        ).fetchall()
    for row in rows:
        row["occurred_at"] = row["occurred_at"].isoformat()
    return rows
