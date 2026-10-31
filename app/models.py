from typing import List, Optional

from werkzeug.security import generate_password_hash, check_password_hash

from app.database import get_connection


# ---------- Usuários ----------

def create_user(username: str, password: str) -> dict:
    """Cria um usuário com a senha hasheada. Retorna o usuário criado."""
    password_hash = generate_password_hash(password)
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, username, created_at FROM users WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)


def get_user_by_username(username: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Devolve o usuário se a senha conferir; None caso contrário."""
    user = get_user_by_username(username)
    if not user:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    return {"id": user["id"], "username": user["username"]}


# ---------- Matérias (por usuário) ----------

def create_subject(user_id: int, name: str) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO subjects (user_id, name) VALUES (?, ?)",
            (user_id, name),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM subjects WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)


def list_subjects(user_id: int) -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM subjects WHERE user_id = ? ORDER BY name",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_subject(user_id: int, subject_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM subjects WHERE id = ? AND user_id = ?",
            (subject_id, user_id),
        ).fetchone()
        return dict(row) if row else None


def update_subject(user_id: int, subject_id: int, new_name: str) -> Optional[dict]:
    with get_connection() as conn:
        conn.execute(
            "UPDATE subjects SET name = ? WHERE id = ? AND user_id = ?",
            (new_name, subject_id, user_id),
        )
        conn.commit()
        return get_subject(user_id, subject_id)


def delete_subject(user_id: int, subject_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM subjects WHERE id = ? AND user_id = ?",
            (subject_id, user_id),
        )
        conn.commit()
        return cursor.rowcount > 0


# ---------- Sessões (por usuário) ----------

def create_session(
    user_id: int,
    subject_id: int,
    duration_minutes: int,
    notes: Optional[str] = None,
) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO study_sessions (user_id, subject_id, duration_minutes, notes)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, subject_id, duration_minutes, notes),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM study_sessions WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)


def list_sessions(user_id: int) -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.id, s.subject_id, sub.name AS subject_name,
                   s.duration_minutes, s.studied_at, s.notes
            FROM study_sessions s
            JOIN subjects sub ON sub.id = s.subject_id
            WHERE s.user_id = ?
            ORDER BY s.studied_at DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_session(user_id: int, session_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM study_sessions WHERE id = ? AND user_id = ?",
            (session_id, user_id),
        ).fetchone()
        return dict(row) if row else None


def update_session(
    user_id: int,
    session_id: int,
    duration_minutes: int,
    notes: Optional[str],
) -> Optional[dict]:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE study_sessions
            SET duration_minutes = ?, notes = ?
            WHERE id = ? AND user_id = ?
            """,
            (duration_minutes, notes, session_id, user_id),
        )
        conn.commit()
        return get_session(user_id, session_id)


def delete_session(user_id: int, session_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM study_sessions WHERE id = ? AND user_id = ?",
            (session_id, user_id),
        )
        conn.commit()
        return cursor.rowcount > 0


# ---------- Relatórios (por usuário, com filtro opcional) ----------

def report_by_subject(
    user_id: int,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> List[dict]:
    query = """
        SELECT sub.name AS subject_name,
               COUNT(*) AS total_sessions,
               SUM(s.duration_minutes) AS total_minutes
        FROM study_sessions s
        JOIN subjects sub ON sub.id = s.subject_id
        WHERE s.user_id = ?
    """
    params = [user_id]

    if start:
        query += " AND date(s.studied_at) >= date(?)"
        params.append(start)
    if end:
        query += " AND date(s.studied_at) <= date(?)"
        params.append(end)

    query += " GROUP BY sub.id ORDER BY total_minutes DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def weekly_report(
    user_id: int,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> List[dict]:
    query = """
        SELECT strftime('%Y-%W', studied_at) AS week,
               COUNT(*) AS total_sessions,
               SUM(duration_minutes) AS total_minutes
        FROM study_sessions
        WHERE user_id = ?
    """
    params = [user_id]

    if start:
        query += " AND date(studied_at) >= date(?)"
        params.append(start)
    if end:
        query += " AND date(studied_at) <= date(?)"
        params.append(end)

    query += " GROUP BY week ORDER BY week DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def sessions_for_export(
    user_id: int,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> List[dict]:
    query = """
        SELECT s.id,
               s.studied_at,
               sub.name AS subject_name,
               s.duration_minutes,
               s.notes
        FROM study_sessions s
        JOIN subjects sub ON sub.id = s.subject_id
        WHERE s.user_id = ?
    """
    params = [user_id]

    if start:
        query += " AND date(s.studied_at) >= date(?)"
        params.append(start)
    if end:
        query += " AND date(s.studied_at) <= date(?)"
        params.append(end)

    query += " ORDER BY s.studied_at DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]