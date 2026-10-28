from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import models

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    subjects = models.list_subjects()
    sessions = models.list_sessions()
    return render_template("index.html", subjects=subjects, sessions=sessions)


@bp.route("/subjects", methods=["POST"])
def add_subject():
    name = request.form.get("name", "").strip()
    if not name:
        flash("O nome da matéria não pode ser vazio.")
        return redirect(url_for("main.index"))

    try:
        models.create_subject(name)
    except Exception:
        flash("Essa matéria já existe.")
    return redirect(url_for("main.index"))


@bp.route("/sessions", methods=["POST"])
def add_session():
    subject_id = request.form.get("subject_id")
    duration = request.form.get("duration_minutes")
    notes = request.form.get("notes", "").strip() or None

    if not subject_id or not duration:
        flash("Preencha a matéria e a duração.")
        return redirect(url_for("main.index"))

    try:
        models.create_session(
            subject_id=int(subject_id),
            duration_minutes=int(duration),
            notes=notes,
        )
    except Exception as e:
        flash(f"Erro ao registrar sessão: {e}")

    return redirect(url_for("main.index"))