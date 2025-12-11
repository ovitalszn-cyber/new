"""
Authentication control-plane database utilities.

This module manages persistent storage for users, API keys, plans, and
usage logs. It provides synchronous helpers that can be wrapped in async
contexts when needed, keeping dependencies minimal while making it easy
to migrate to PostgreSQL later.
"""

from __future__ import annotations

import os
import sqlite3
import threading
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from structlog import get_logger

logger = get_logger(__name__)

AUTH_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "auth.db"


class AuthDB:
    """Simple SQLite-backed control-plane storage."""

    def __init__(self, db_path: Path = AUTH_DB_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()
        self._ensure_user_columns()
        self._ensure_usage_columns()
        self._ensure_default_plans()
        self._bootstrap_legacy_keys()

    # ... (Low-level helpers) ...

    # ... (Schema bootstrap) ...

    # ... (ensure_user_columns) ...

    def _ensure_usage_columns(self) -> None:
        """Ensure latency_ms column exists on usage_logs table."""
        with self._lock:
            with self._get_conn() as conn:
                cursor = conn.execute("PRAGMA table_info(usage_logs)")
                columns = {row["name"] for row in cursor.fetchall()}
                if "latency_ms" not in columns:
                    conn.execute("ALTER TABLE usage_logs ADD COLUMN latency_ms INTEGER")

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------
    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _execute(self, query: str, params: tuple = (), fetchone: bool = False, fetchall: bool = False) -> Any:
        with self._lock:
            with self._get_conn() as conn:
                cursor = conn.execute(query, params)
                if fetchone:
                    return cursor.fetchone()
                if fetchall:
                    return cursor.fetchall()
                return None

    @staticmethod
    def _format_timestamp(dt: datetime) -> str:
        """Format datetime for SQLite comparisons."""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Schema bootstrap
    # ------------------------------------------------------------------
    def _init_db(self) -> None:
        schema_statements = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                plan TEXT NOT NULL DEFAULT 'free',
                status TEXT NOT NULL DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                monthly_quota INTEGER NOT NULL,
                rate_limit_per_min INTEGER NOT NULL,
                price_monthly REAL NOT NULL,
                metadata TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                key_prefix TEXT NOT NULL,
                key_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS usage_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                api_key_id TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                status_code INTEGER,
                credits_used INTEGER NOT NULL DEFAULT 1,
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (api_key_id) REFERENCES api_keys(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS monthly_usage (
                user_id TEXT NOT NULL,
                key_type TEXT NOT NULL,
                year_month TEXT NOT NULL,
                requests INTEGER NOT NULL DEFAULT 0,
                credits INTEGER NOT NULL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, key_type, year_month)
            )
            """,
        ]

        with self._lock:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                for statement in schema_statements:
                    cursor.execute(statement)
                conn.commit()

    def _ensure_user_columns(self) -> None:
        """Ensure optional columns exist on users table for OAuth metadata."""
        with self._lock:
            with self._get_conn() as conn:
                cursor = conn.execute("PRAGMA table_info(users)")
                columns = {row["name"] for row in cursor.fetchall()}
                if "google_id" not in columns:
                    conn.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
                if "name" not in columns:
                    conn.execute("ALTER TABLE users ADD COLUMN name TEXT")

                # Enforce uniqueness on google_id using an index (ALTER TABLE cannot add UNIQUE)
                conn.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_id
                    ON users(google_id)
                    WHERE google_id IS NOT NULL
                    """
                )
                conn.commit()

    def _ensure_default_plans(self) -> None:
        default_plans = [
            ("free", 1000, 10, 0.0, '{"label": "Free"}'),
            ("starter", 10000, 100, 49.0, '{"label": "Starter"}'),
            ("pro", 100000, 500, 199.0, '{"label": "Pro"}'),
        ]
        with self._lock:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                for plan in default_plans:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO plans (id, monthly_quota, rate_limit_per_min, price_monthly, metadata)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        plan,
                    )
                conn.commit()

    def _bootstrap_legacy_keys(self) -> None:
        """Import legacy environment keys into the control-plane database."""
        legacy_vars = []
        admin_key = os.getenv("ADMIN_API_KEY")
        if admin_key:
            legacy_vars.append("admin:" + admin_key)

        for i in range(1, 11):
            value = os.getenv(f"API_KEY_{i}")
            if value:
                legacy_vars.append(value)

        if not legacy_vars:
            return

        for raw in legacy_vars:
            parts = raw.split(":")
            if len(parts) < 2:
                continue
            name, key = parts[0], parts[1]
            status = parts[2] if len(parts) > 2 else "active"
            rate_limit = int(parts[3]) if len(parts) > 3 else 1000

            email = f"{name}@legacy.kashrock"
            plan = self._plan_from_rate_limit(rate_limit)
            user = self.get_user_by_email(email)
            if not user:
                password = secrets.token_urlsafe(16)
                user = self.create_user(email=email, password=password, plan=plan)

            # Skip if key already exists
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            existing = self.get_api_key_record_by_hash(key_hash)
            if existing:
                continue

            key_type = "live"
            key_prefix = key[:12]
            key_id = str(uuid.uuid4())
            with self._lock:
                with self._get_conn() as conn:
                    conn.execute(
                        """
                        INSERT INTO api_keys (id, user_id, key_hash, key_prefix, key_type, status, name)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            key_id,
                            user["id"],
                            key_hash,
                            key_prefix,
                            key_type,
                            status,
                            name,
                        ),
                    )
                    conn.commit()
            logger.info("Bootstrapped legacy API key", name=name, plan=plan, status=status)

    def _plan_from_rate_limit(self, rate_limit: int) -> str:
        if rate_limit >= 500:
            return "pro"
        if rate_limit >= 100:
            return "starter"
        return "free"

    # ------------------------------------------------------------------
    # Password utilities
    # ------------------------------------------------------------------
    def hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return f"{salt.hex()}${hash_bytes.hex()}"

    def verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            salt_hex, hash_hex = stored_hash.split("$")
        except ValueError:
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return secrets.compare_digest(expected, actual)

    # ------------------------------------------------------------------
    # User management
    # ------------------------------------------------------------------
    def create_user(
        self,
        email: str,
        password: str,
        plan: str = "free",
        status: str = "active",
        google_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(password)
        now = datetime.utcnow().isoformat()
        with self._lock:
            with self._get_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO users (id, email, password_hash, plan, status, created_at, updated_at, google_id, name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, email, password_hash, plan, status, now, now, google_id, name),
                )
                conn.commit()
        return {
            "id": user_id,
            "email": email,
            "google_id": google_id,
            "name": name,
            "plan": plan,
            "status": status,
            "created_at": now,
        }

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        row = self._execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
            fetchone=True,
        )
        return dict(row) if row else None

    def get_user_by_google_id(self, google_id: str) -> Optional[Dict[str, Any]]:
        row = self._execute(
            "SELECT * FROM users WHERE google_id = ?",
            (google_id,),
            fetchone=True,
        )
        return dict(row) if row else None

    def update_user_profile(self, user_id: str, google_id: Optional[str], name: Optional[str]) -> None:
        updates = []
        params: list[Any] = []
        if google_id:
            updates.append("google_id = ?")
            params.append(google_id)
        if name:
            updates.append("name = ?")
            params.append(name)
        if not updates:
            return
        updates.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        self._execute(query, tuple(params))

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        row = self._execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
            fetchone=True,
        )
        return dict(row) if row else None

    def update_user_plan(self, user_id: str, plan: str) -> None:
        now = datetime.utcnow().isoformat()
        self._execute(
            "UPDATE users SET plan = ?, updated_at = ? WHERE id = ?",
            (plan, now, user_id),
        )

    # ------------------------------------------------------------------
    # API key management
    # ------------------------------------------------------------------
    def create_api_key(
        self,
        user_id: str,
        key_type: str = "live",
        name: Optional[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        token = secrets.token_urlsafe(32)
        raw_key = f"kr_{key_type}_{token}"
        key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        key_prefix = raw_key[:12]
        key_id = str(uuid.uuid4())
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()
        now = datetime.utcnow().isoformat()

        with self._lock:
            with self._get_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO api_keys (id, user_id, key_hash, key_prefix, key_type, status, name, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?)
                    """,
                    (key_id, user_id, key_hash, key_prefix, key_type, name, now, expires_at),
                )
                conn.commit()

        return {
            "id": key_id,
            "plain_key": raw_key,
            "key_type": key_type,
            "key_prefix": key_prefix,
            "expires_at": expires_at,
        }

    def get_api_key_record_by_hash(self, key_hash: str) -> Optional[Dict[str, Any]]:
        row = self._execute(
            """
            SELECT ak.*, u.email AS user_email, u.plan AS user_plan, u.status AS user_status, p.monthly_quota, p.rate_limit_per_min
            FROM api_keys ak
            JOIN users u ON ak.user_id = u.id
            LEFT JOIN plans p ON u.plan = p.id
            WHERE ak.key_hash = ?
            """,
            (key_hash,),
            fetchone=True,
        )
        return dict(row) if row else None

    def update_last_used(self, api_key_id: str) -> None:
        now = datetime.utcnow().isoformat()
        self._execute(
            "UPDATE api_keys SET last_used_at = ?, status = status WHERE id = ?",
            (now, api_key_id),
        )

    def deactivate_key(self, api_key_id: str) -> None:
        self._execute(
            "UPDATE api_keys SET status = 'revoked' WHERE id = ?",
            (api_key_id,),
        )

    def delete_api_key(self, api_key_id: str) -> None:
        self._execute(
            "DELETE FROM api_keys WHERE id = ?",
            (api_key_id,),
        )

    def list_api_keys(self) -> list[Dict[str, Any]]:
        rows = self._execute(
            """
            SELECT ak.*, u.email AS user_email, u.plan AS user_plan, u.status AS user_status,
                   p.monthly_quota, p.rate_limit_per_min
            FROM api_keys ak
            JOIN users u ON ak.user_id = u.id
            LEFT JOIN plans p ON u.plan = p.id
            ORDER BY ak.created_at DESC
            """,
            fetchall=True,
        )
        return [dict(row) for row in rows] if rows else []

    def get_api_key_by_id(self, key_id: str) -> Optional[Dict[str, Any]]:
        row = self._execute(
            """
            SELECT ak.*, u.email, u.plan AS user_plan, u.status AS user_status,
                   p.monthly_quota, p.rate_limit_per_min
            FROM api_keys ak
            JOIN users u ON ak.user_id = u.id
            LEFT JOIN plans p ON u.plan = p.id
            WHERE ak.id = ?
            """,
            (key_id,),
            fetchone=True,
        )
        return dict(row) if row else None

    def get_api_keys_for_user(self, user_id: str) -> list[Dict[str, Any]]:
        rows = self._execute(
            """
            SELECT *
            FROM api_keys
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
            fetchall=True,
        )
        return [dict(row) for row in rows] if rows else []

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        row = self._execute(
            "SELECT * FROM plans WHERE id = ?",
            (plan_id,),
            fetchone=True,
        )
        return dict(row) if row else None

    # ------------------------------------------------------------------
    # Usage logging
    # ------------------------------------------------------------------
    def log_usage(
        self,
        user_id: str,
        api_key_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        credits_used: int,
        latency_ms: Optional[int] = None,
    ) -> None:
        log_id = str(uuid.uuid4())
        self._execute(
            """
            INSERT INTO usage_logs (id, user_id, api_key_id, endpoint, method, status_code, credits_used, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (log_id, user_id, api_key_id, endpoint, method, status_code, credits_used, latency_ms),
        )

    def increment_monthly_usage(self, user_id: str, key_type: str, credits: int) -> None:
        year_month = datetime.utcnow().strftime("%Y-%m")
        self._execute(
            """
            INSERT INTO monthly_usage (user_id, key_type, year_month, requests, credits, updated_at)
            VALUES (?, ?, ?, 1, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, key_type, year_month)
            DO UPDATE SET
                requests = requests + 1,
                credits = credits + excluded.credits,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, key_type, year_month, credits),
        )

    def get_monthly_usage(self, user_id: str, key_type: str) -> Dict[str, int]:
        year_month = datetime.utcnow().strftime("%Y-%m")
        row = self._execute(
            """
            SELECT requests, credits FROM monthly_usage
            WHERE user_id = ? AND key_type = ? AND year_month = ?
            """,
            (user_id, key_type, year_month),
            fetchone=True,
        )
        if not row:
            return {"requests": 0, "credits": 0}
        return {"requests": row["requests"], "credits": row["credits"]}

    def get_usage_summary_since(self, user_id: str, start_time: datetime) -> Dict[str, int]:
        """Aggregate usage stats for a user since a given timestamp."""
        start = self._format_timestamp(start_time)
        row = self._execute(
            """
            SELECT
                COUNT(*) AS total_requests,
                SUM(CASE WHEN status_code BETWEEN 200 AND 299 THEN 1 ELSE 0 END) AS successful_requests,
                SUM(CASE WHEN status_code BETWEEN 400 AND 499 THEN 1 ELSE 0 END) AS client_errors,
                SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) AS server_errors
            FROM usage_logs
            WHERE user_id = ? AND requested_at >= ?
            """,
            (user_id, start),
            fetchone=True,
        )
        if not row:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "client_errors": 0,
                "server_errors": 0,
            }
        return {
            "total_requests": row["total_requests"] or 0,
            "successful_requests": row["successful_requests"] or 0,
            "client_errors": row["client_errors"] or 0,
            "server_errors": row["server_errors"] or 0,
        }

    def get_endpoint_usage_since(
        self,
        user_id: str,
        start_time: datetime,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Return aggregated counts per endpoint since a timestamp."""
        start = self._format_timestamp(start_time)
        rows = self._execute(
            """
            SELECT endpoint, COUNT(*) AS count
            FROM usage_logs
            WHERE user_id = ? AND requested_at >= ?
            GROUP BY endpoint
            ORDER BY count DESC
            LIMIT ?
            """,
            (user_id, start, limit),
            fetchall=True,
        )
        return [dict(row) for row in rows] if rows else []

    def get_usage_logs_since(
        self,
        user_id: str,
        start_time: datetime,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Return recent usage log entries for a user."""
        start = self._format_timestamp(start_time)
        rows = self._execute(
            """
            SELECT
                ul.id,
                ul.endpoint,
                ul.method,
                ul.status_code,
                ul.credits_used,
                ul.requested_at,
                ul.api_key_id,
                ul.latency_ms,
                ak.key_prefix
            FROM usage_logs ul
            LEFT JOIN api_keys ak ON ul.api_key_id = ak.id
            WHERE ul.user_id = ? AND ul.requested_at >= ?
            ORDER BY ul.requested_at DESC
            LIMIT ?
            """,
            (user_id, start, limit),
            fetchall=True,
        )
        return [dict(row) for row in rows] if rows else []


    def get_top_users_by_usage(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return top users by total credit usage."""
        rows = self._execute(
            """
            SELECT 
                u.id as user_id,
                u.email,
                u.google_id,
                COUNT(ul.id) as total_requests,
                SUM(ul.credits_used) as total_credits
            FROM usage_logs ul
            JOIN users u ON ul.user_id = u.id
            GROUP BY u.email, u.google_id
            ORDER BY total_credits DESC
            LIMIT ?
            """,
            (limit,),
            fetchall=True,
        )
        return [dict(row) for row in rows] if rows else []


    def get_user_endpoint_stats(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Return most used endpoints for a specific user."""
        rows = self._execute(
            """
            SELECT 
                endpoint,
                method,
                COUNT(*) as count,
                SUM(credits_used) as total_credits
            FROM usage_logs
            WHERE user_id = ?
            GROUP BY endpoint, method
            ORDER BY count DESC
            LIMIT ?
            """,
            (user_id, limit),
            fetchall=True,
        )
        return [dict(row) for row in rows] if rows else []

auth_db = AuthDB()
"""
Global auth database instance imported by control-plane services.
"""
