from typing import List, Optional
from app.database import get_connection


# ---------- Matérias ----------

def create_subject(name: str) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO subjects (name) VALUES (?)", (name,)
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM subjects WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)


def list_subjects() -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM subjects ORDER BY name").fetchall()
        return [dict(r) for r in rows]


def get_subject(subject_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM subjects WHERE id = ?", (subject_id,)
        ).fetchone()
        return dict(row) if row else None


# ---------- Sessões de estudo ----------

def create_session(subject_id: int, duration_minutes: int, notes: Optional[str] = None) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO study_sessions (subject_id, duration_minutes, notes)
            VALUES (?, ?, ?)
            """,
            (subject_id, duration_minutes, notes),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM study_sessions WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)


def list_sessions() -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.id, s.subject_id, sub.name AS subject_name,
                   s.duration_minutes, s.studied_at, s.notes
            FROM study_sessions s
            JOIN subjects sub ON sub.id = s.subject_id
            ORDER BY s.studied_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]