from db import connect_db


def create_event(event):
    with connect_db() as conn:
        conn.execute(
            """INSERT INTO http_events (method, path, status_code, event_type)
               VALUES (%s, %s, %s, %s)""",
            (event["method"], event["path"], event["status_code"], event["event_type"]),
        )


def list_events(event_type=None, path=None, status_code=None):
    with connect_db() as conn:
        conditions = []
        params = []
        if event_type:
            conditions.append("event_type = %s")
            params.append(event_type)
        if path:
            conditions.append("path ILIKE %s")
            params.append(f"%{path}%")
        if status_code is not None:
            conditions.append("status_code = %s")
            params.append(status_code)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        query = f"SELECT * FROM http_events {where_clause} ORDER BY id DESC LIMIT 50"
        rows = conn.execute(query, tuple(params)).fetchall()
    for row in rows:
        row["occurred_at"] = row["occurred_at"].isoformat()
    return rows
