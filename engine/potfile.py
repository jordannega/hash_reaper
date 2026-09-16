"""SQLite potfile: every cracked hash is remembered."""
import sqlite3
import time
from pathlib import Path


class Potfile:
    def __init__(self, path: Path = Path("reaper.pot")):
        self.db = sqlite3.connect(str(path))
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS cracks (
                hash TEXT,
                algo TEXT,
                plaintext TEXT,
                salt TEXT,
                found_at REAL,
                PRIMARY KEY (hash, salt)
            )
        """)
        self.db.commit()

    def lookup(self, hash_str: str, salt: str = ""):
        row = self.db.execute(
            "SELECT plaintext FROM cracks WHERE hash=? AND salt=?",
            (hash_str, salt),
        ).fetchone()
        return row[0] if row else None

    def save(self, hash_str: str, algo: str, plaintext: str, salt: str = ""):
        self.db.execute(
            "INSERT OR REPLACE INTO cracks VALUES (?, ?, ?, ?, ?)",
            (hash_str, algo, plaintext, salt, time.time()),
        )
        self.db.commit()

    def stats(self):
        row = self.db.execute(
            "SELECT COUNT(*), MIN(found_at), MAX(found_at) FROM cracks"
        ).fetchone()
        return {"total": row[0], "first": row[1], "last": row[2]}