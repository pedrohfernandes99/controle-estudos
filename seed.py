"""Populate the database with sample data for demonstration.

Usage:
    python seed.py

Creates the user 'demo' (password 'demo1234') with 5 subjects and 12
sessions spread across the last 4 weeks. If 'demo' already exists,
their data is wiped and recreated.
"""

from datetime import datetime, timedelta

from app import models
from app.database import get_connection, init_db


def main() -> None:
    init_db()

    if models.get_user_by_username("demo"):
        with get_connection() as conn:
            conn.execute("DELETE FROM users WHERE username = 'demo'")
            conn.commit()
        print("Previous 'demo' data deleted.")

    user = models.create_user("demo", "demo1234")
    user_id = user["id"]
    print(f"Created 'demo' (id={user_id}).")

    subjects_data = [
        "Calculus I",
        "Data Structures",
        "Software Engineering",
        "Databases",
        "Physics I",
    ]
    subjects = {}
    for name in subjects_data:
        s = models.create_subject(user_id, name)
        subjects[name] = s["id"]
    print(f"{len(subjects)} subjects created.")

    # (days_ago, subject, duration_minutes, notes)
    sessions_data = [
        (21, "Calculus I", 60, "Limits and derivatives review"),
        (18, "Data Structures", 90, "Linked list implementation"),
        (16, "Software Engineering", 45, "Reading ch. 3 — agile methodologies"),
        (14, "Databases", 60, "Final project ER modeling"),
        (12, "Calculus I", 90, "Integrals exercises"),
        (10, "Physics I", 30, "Kinematics exercises"),
        (8, "Data Structures", 75, "Binary search trees"),
        (6, "Software Engineering", 60, "Project requirements review"),
        (5, "Databases", 45, "Normalization — 1NF, 2NF, 3NF"),
        (3, "Calculus I", 60, "Exam 1 prep"),
        (2, "Physics I", 45, "Vectors review"),
        (1, "Data Structures", 90, "Sorting algorithms"),
    ]

    now = datetime.now()
    for days_ago, subject_name, duration, notes in sessions_data:
        studied_at = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO study_sessions "
                "(user_id, subject_id, duration_minutes, studied_at, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, subjects[subject_name], duration, studied_at, notes),
            )
            conn.commit()

    total = sum(s[2] for s in sessions_data)
    print(f"{len(sessions_data)} sessions created.")
    print(f"Total: {total} minutes ({total/60:.1f} hours).")
    print("Ready! Log in with 'demo' / 'demo1234'.")


if __name__ == "__main__":
    main()