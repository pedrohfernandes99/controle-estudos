import sqlite3

import pytest

from app import models


# ---------- Matérias ----------

def test_create_subject(db, user):
    subject = models.create_subject(user["id"], "Cálculo I")
    assert subject["id"] == 1
    assert subject["name"] == "Cálculo I"
    assert subject["user_id"] == user["id"]


def test_create_duplicate_subject_raises(db, user):
    models.create_subject(user["id"], "Cálculo I")
    with pytest.raises(sqlite3.IntegrityError):
        models.create_subject(user["id"], "Cálculo I")


def test_same_name_different_users_allowed(db, user):
    other = models.create_user("outro", "senha123")
    models.create_subject(user["id"], "Cálculo I")
    subject2 = models.create_subject(other["id"], "Cálculo I")
    assert subject2["user_id"] == other["id"]


def test_list_subjects_only_own(db, user):
    other = models.create_user("outro", "senha123")
    models.create_subject(user["id"], "Cálculo I")
    models.create_subject(other["id"], "Física")
    subjects = models.list_subjects(user["id"])
    assert len(subjects) == 1
    assert subjects[0]["name"] == "Cálculo I"


def test_list_subjects_alphabetical(db, user):
    models.create_subject(user["id"], "Física")
    models.create_subject(user["id"], "Cálculo I")
    subjects = models.list_subjects(user["id"])
    assert subjects[0]["name"] == "Cálculo I"
    assert subjects[1]["name"] == "Física"


def test_get_subject(db, user):
    created = models.create_subject(user["id"], "Cálculo I")
    found = models.get_subject(user["id"], created["id"])
    assert found["name"] == "Cálculo I"


def test_get_subject_not_found(db, user):
    assert models.get_subject(user["id"], 999) is None


def test_get_subject_of_other_user_returns_none(db, user):
    other = models.create_user("outro", "senha123")
    subject = models.create_subject(other["id"], "Cálculo I")
    assert models.get_subject(user["id"], subject["id"]) is None


def test_update_subject(db, user):
    subject = models.create_subject(user["id"], "Cálculo I")
    updated = models.update_subject(user["id"], subject["id"], "Cálculo II")
    assert updated["name"] == "Cálculo II"


def test_delete_subject(db, user):
    subject = models.create_subject(user["id"], "Cálculo I")
    assert models.delete_subject(user["id"], subject["id"]) is True
    assert models.get_subject(user["id"], subject["id"]) is None


def test_delete_subject_not_found(db, user):
    assert models.delete_subject(user["id"], 999) is False


def test_delete_subject_of_other_user_returns_false(db, user):
    other = models.create_user("outro", "senha123")
    subject = models.create_subject(other["id"], "Cálculo I")
    assert models.delete_subject(user["id"], subject["id"]) is False
    assert models.get_subject(other["id"], subject["id"]) is not None


# ---------- Sessões ----------

def test_create_session(db, user):
    subject = models.create_subject(user["id"], "Cálculo I")
    session = models.create_session(user["id"], subject["id"], 60, "Revisão")
    assert session["duration_minutes"] == 60
    assert session["notes"] == "Revisão"
    assert session["subject_id"] == subject["id"]
    assert session["user_id"] == user["id"]


def test_list_sessions_includes_subject_name(db, user):
    subject = models.create_subject(user["id"], "Cálculo I")
    models.create_session(user["id"], subject["id"], 60)
    sessions = models.list_sessions(user["id"])
    assert len(sessions) == 1
    assert sessions[0]["subject_name"] == "Cálculo I"


def test_list_sessions_only_own(db, user):
    other = models.create_user("outro", "senha123")
    s1 = models.create_subject(user["id"], "Cálculo I")
    s2 = models.create_subject(other["id"], "Física")
    models.create_session(user["id"], s1["id"], 60)
    models.create_session(other["id"], s2["id"], 30)
    sessions = models.list_sessions(user["id"])
    assert len(sessions) == 1
    assert sessions[0]["subject_name"] == "Cálculo I"


def test_update_session(db, user):
    subject = models.create_subject(user["id"], "Cálculo I")
    session = models.create_session(user["id"], subject["id"], 60)
    updated = models.update_session(user["id"], session["id"], 90, "Nova obs")
    assert updated["duration_minutes"] == 90
    assert updated["notes"] == "Nova obs"


def test_delete_session(db, user):
    subject = models.create_subject(user["id"], "Cálculo I")
    session = models.create_session(user["id"], subject["id"], 60)
    assert models.delete_session(user["id"], session["id"]) is True
    assert models.get_session(user["id"], session["id"]) is None


def test_delete_session_of_other_user_returns_false(db, user):
    other = models.create_user("outro", "senha123")
    subject = models.create_subject(other["id"], "Cálculo I")
    session = models.create_session(other["id"], subject["id"], 60)
    assert models.delete_session(user["id"], session["id"]) is False


def test_delete_subject_cascades_sessions(db, user):
    subject = models.create_subject(user["id"], "Cálculo I")
    models.create_session(user["id"], subject["id"], 60)
    models.create_session(user["id"], subject["id"], 30)
    models.delete_subject(user["id"], subject["id"])
    assert models.list_sessions(user["id"]) == []


# ---------- Relatórios ----------

def test_report_by_subject(db, user):
    subject = models.create_subject(user["id"], "Cálculo I")
    models.create_session(user["id"], subject["id"], 60)
    models.create_session(user["id"], subject["id"], 30)
    report = models.report_by_subject(user["id"])
    assert len(report) == 1
    assert report[0]["total_minutes"] == 90
    assert report[0]["total_sessions"] == 2


def test_weekly_report(db, user):
    subject = models.create_subject(user["id"], "Cálculo I")
    models.create_session(user["id"], subject["id"], 60)
    weekly = models.weekly_report(user["id"])
    assert len(weekly) == 1
    assert weekly[0]["total_minutes"] == 60


def test_sessions_for_export_only_own(db, user):
    other = models.create_user("outro", "senha123")
    s1 = models.create_subject(user["id"], "Cálculo I")
    s2 = models.create_subject(other["id"], "Física")
    models.create_session(user["id"], s1["id"], 60)
    models.create_session(other["id"], s2["id"], 30)
    export = models.sessions_for_export(user["id"])
    assert len(export) == 1
    assert export[0]["subject_name"] == "Cálculo I"