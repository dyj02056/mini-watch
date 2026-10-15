from db import connect_db


def create_observation(observation):
    with connect_db() as conn:
        conn.execute(
            """INSERT INTO detection_observations (id, started_at, after_id)
               VALUES (%s, %s, %s)""",
            (observation["id"], observation["started_at"], observation["after_id"]),
        )


def current_observation():
    with connect_db() as conn:
        row = conn.execute(
            """SELECT id, started_at, after_id FROM detection_observations
               ORDER BY sequence DESC LIMIT 1"""
        ).fetchone()
    if row:
        row["started_at"] = row["started_at"].isoformat(timespec="microseconds")
    return row
