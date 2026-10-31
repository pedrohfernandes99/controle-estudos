import csv
import io

from flask import Blueprint, render_template, request, redirect, url_for, flash, session

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
    start = request.args.get("start") or None
    end = request.args.get("end") or None

    report_data = models.report_by_subject(start, end)
    grand_total = sum(r["total_minutes"] for r in report_data) if report_data else 0

    return render_template(
        "report.html",
        report=report_data,
        grand_total=grand_total,
        start=start,
        end=end,
    )

    
@bp.route("/report/weekly")
def report_weekly():
    data = models.weekly_report()
    grand_total = sum(r["total_minutes"] for r in data) if data else 0
    return render_template("report_weekly.html", report=data, grand_total=grand_total)

    
# ---------- Exportação CSV ----------

@bp.route("/export/sessions.csv")
def export_sessions_csv():
    start = request.args.get("start") or None
    end = request.args.get("end") or None

    sessions = models.sessions_for_export(start, end)

    # io.StringIO = "arquivo" de texto na memória (não grava no disco)
    buffer = io.StringIO()
    # newline="" evita linhas em branco extras no Windows
    writer = csv.writer(buffer, delimiter=";", lineterminator="\n")

    # Cabeçalho
    writer.writerow(["id", "data", "materia", "duracao_minutos", "observacoes"])

    # Linhas
    for s in sessions:
        writer.writerow([
            s["id"],
            s["studied_at"],
            s["subject_name"],
            s["duration_minutes"],
            s["notes"] or "",
        ])

    # Devolve o conteúdo como download
    from flask import Response
    return Response(
        buffer.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=estudos.csv",
        },
    )

    
# ---------- Autenticação ----------

@bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if not username or not password:
            flash("Preencha usuário e senha.")
        elif len(password) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.")
        elif password != password2:
            flash("As senhas não conferem.")
        elif models.get_user_by_username(username):
            flash("Este usuário já existe.")
        else:
            try:
                user = models.create_user(username, password)
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                flash("Conta criada com sucesso.")
                return redirect(url_for("main.index"))
            except Exception as e:
                flash(f"Erro ao criar conta: {e}")

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = models.authenticate_user(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Bem-vindo, {user['username']}!")
            return redirect(url_for("main.index"))
        else:
            flash("Usuário ou senha incorretos.")

    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Você saiu.")
    return redirect(url_for("main.index"))