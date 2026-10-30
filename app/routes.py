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

    
# ---------- Edição e exclusão de matérias ----------

@bp.route("/subjects/<int:subject_id>/edit", methods=["GET", "POST"])
def edit_subject(subject_id):
    subject = models.get_subject(subject_id)
    if not subject:
        flash("Matéria não encontrada.")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        new_name = request.form.get("name", "").strip()
        if not new_name:
            flash("O nome não pode ser vazio.")
        else:
            try:
                models.update_subject(subject_id, new_name)
                flash("Matéria atualizada.")
                return redirect(url_for("main.index"))
            except Exception:
                flash("Já existe outra matéria com esse nome.")

    return render_template("edit_subject.html", subject=subject)


@bp.route("/subjects/<int:subject_id>/delete", methods=["POST"])
def delete_subject(subject_id):
    if models.delete_subject(subject_id):
        flash("Matéria apagada.")
    else:
        flash("Matéria não encontrada.")
    return redirect(url_for("main.index"))


# ---------- Edição e exclusão de sessões ----------

@bp.route("/sessions/<int:session_id>/edit", methods=["GET", "POST"])
def edit_session(session_id):
    session = models.get_session(session_id)
    if not session:
        flash("Sessão não encontrada.")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        duration = request.form.get("duration_minutes")
        notes = request.form.get("notes", "").strip() or None
        if not duration:
            flash("Informe a duração.")
        else:
            models.update_session(session_id, int(duration), notes)
            flash("Sessão atualizada.")
            return redirect(url_for("main.index"))

    return render_template("edit_session.html", session=session)


@bp.route("/sessions/<int:session_id>/delete", methods=["POST"])
def delete_session(session_id):
    if models.delete_session(session_id):
        flash("Sessão apagada.")
    else:
        flash("Sessão não encontrada.")
    return redirect(url_for("main.index"))


# ---------- Relatório ----------

@bp.route("/report")
def report():
    from app.database import get_connection
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT sub.name AS subject_name,
                   COUNT(*) AS total_sessions,
                   SUM(s.duration_minutes) AS total_minutes
            FROM study_sessions s
            JOIN subjects sub ON sub.id = s.subject_id
            GROUP BY sub.id
            ORDER BY total_minutes DESC
            """
        ).fetchall()
        report_data = [dict(r) for r in rows]

        grand_total = sum(r["total_minutes"] for r in report_data) if report_data else 0

    return render_template("report.html", report=report_data, grand_total=grand_total)

    
@bp.route("/report/weekly")
def report_weekly():
    data = models.weekly_report()
    grand_total = sum(r["total_minutes"] for r in data) if data else 0
    return render_template("report_weekly.html", report=data, grand_total=grand_total)