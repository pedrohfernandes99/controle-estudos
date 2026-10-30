import sqlite3

import pytest

from app import models


# ---------- Matérias ----------

def test_create_subject(db):
    subject = models.create_subject("Cálculo I")
    assert subject["id"] == 1
    assert subject["name"] == "Cálculo I"


def test_create_duplicate_subject_raises(db):
    models.create_subject("Cálculo I")
    with pytest.raises(sqlite3.IntegrityError):
        models.create_subject("Cálculo I")


def test_list_subjects(db):
    models.create_subject("Física")
    models.create_subject("Cálculo I")
    subjects = models.list_subjects()
    assert len(subjects) == 2
    # Ordem alfabética: Cálculo I antes de Física
    assert subjects[0]["name"] == "Cálculo I"
    assert subjects[1]["name"] == "Física"


def test_get_subject(db):
    created = models.create_subject("Cálculo I")
    found = models.get_subject(created["id"])
    assert found["name"] == "Cálculo I"


def test_get_subject_not_found(db):
    assert models.get_subject(999) is None


def test_update_subject(db):
    subject = models.create_subject("Cálculo I")
    updated = models.update_subject(subject["id"], "Cálculo II")
    assert updated["name"] == "Cálculo II"


def test_delete_subject(db):
    subject = models.create_subject("Cálculo I")
    assert models.delete_subject(subject["id"]) is True
    assert models.get_subject(subject["id"]) is None


def test_delete_subject_not_found(db):
    assert models.delete_subject(999) is False


# ---------- Sessões ----------

def test_create_session(db):
    subject = models.create_subject("Cálculo I")
    session = models.create_session(subject["id"], 60, "Revisão")
    assert session["duration_minutes"] == 60
    assert session["notes"] == "Revisão"
    assert session["subject_id"] == subject["id"]


def test_list_sessions_includes_subject_name(db):
    subject = models.create_subject("Cálculo I")
    models.create_session(subject["id"], 60)
    sessions = models.list_sessions()
    assert len(sessions) == 1
    assert sessions[0]["subject_name"] == "Cálculo I"


def test_update_session(db):
    subject = models.create_subject("Cálculo I")
    session = models.create_session(subject["id"], 60)
    updated = models.update_session(session["id"], 90, "Nova obs")
    assert updated["duration_minutes"] == 90
    assert updated["notes"] == "Nova obs"


def test_delete_session(db):
    subject = models.create_subject("Cálculo I")
    session = models.create_session(subject["id"], 60)
    assert models.delete_session(session["id"]) is True
    assert models.get_session(session["id"]) is None


def test_delete_subject_cascades_sessions(db):
    subject = models.create_subject("Cálculo I")
    models.create_session(subject["id"], 60)
    models.create_session(subject["id"], 30)
    models.delete_subject(subject["id"])
    assert models.list_sessions() == []