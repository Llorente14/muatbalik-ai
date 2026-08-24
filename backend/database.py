# ── MuatBalik AI — Database helper (SQLite) ──
# Source: PRD §9 "SQLite untuk demo"

import sqlite3
from pathlib import Path
from typing import Generator

DB_PATH = Path(__file__).parent / "db" / "muatbalik.db"
SCHEMA_PATH = Path(__file__).parent / "db" / "schema.sql"


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency — yields a DB connection per request."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Create tables from schema.sql if they don't exist yet."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
