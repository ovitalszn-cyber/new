import json
import sys

from db.auth_db import auth_db


def fetch_table(conn, name: str):
    cur = conn.execute(f"SELECT * FROM {name}")
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def main() -> None:
    """Dump control-plane auth + usage state to JSON on stdout.

    Tables included:
    - users
    - plans
    - api_keys
    - usage_logs
    - monthly_usage
    """
    # Reuse the auth_db connection helper
    conn = auth_db._get_conn()  # type: ignore[attr-defined]
    try:
        payload = {
            "users": fetch_table(conn, "users"),
            "plans": fetch_table(conn, "plans"),
            "api_keys": fetch_table(conn, "api_keys"),
            "usage_logs": fetch_table(conn, "usage_logs"),
            "monthly_usage": fetch_table(conn, "monthly_usage"),
        }
        # Dump to stdout so callers can redirect to a file
        json.dump(payload, sys.stdout, indent=2)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
