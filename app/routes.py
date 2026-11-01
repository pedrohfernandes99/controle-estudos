import csv
import io

from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app import models
from app.auth import login_required, current_user_id

bp = Blueprint("main", __name__)


# ---------- Home ----------

@bp.route("/")
@login_required
def index():
    user_id = current_user_id()
    subjects = models.list_subjects(user_id)
    sessions = models.list_sessions(user_id)
    return render_template("index.html", subjects=subjects, sessions=sessions)


# ---------- Subjects ----------

@bp.route("/subjects", methods=["POST"])
@login_required
def add_subject():
    user_id = current_user_id()
    name = request.form.get("name", "").strip()
    if not name:
        flash("Subject name cannot be empty.")
        return redirect(url_for("main.index"))

    try:
        models.create_subject(user_id, name)
    except Exception:
        flash("This subject already exists.")
    return redirect(url_for("main.index"))


@bp.route("/subjects/<int:subject_id>/edit", methods=["GET", "POST"])
@login_required
def edit_subject(subject_id):
    user_id = current_user_id()
    subject = models.get_subject(user_id, subject_id)
    if not subject:
        flash("Subject not found.")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        new_name = request.form.get("name", "").strip()
        if not new_name:
            flash("Name cannot be empty.")
        else:
            try:
                models.update_subject(user_id, subject_id, new_name)
                flash("Subject updated.")
                return redirect(url_for("main.index"))
            except Exception:
                flash("Another subject with this name already exists.")

    return render_template("edit_subject.html", subject=subject)


@bp.route("/subjects/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete_subject(subject_id):
    user_id = current_user_id()
    if models.delete_subject(user_id, subject_id):
        flash("Subject deleted.")
    else:
        flash("Subject not found.")
    return redirect(url_for("main.index"))


# ---------- Sessions ----------

@bp.route("/sessions", methods=["POST"])
@login_required
def add_session():
    user_id = current_user_id()
    subject_id = request.form.get("subject_id")
    duration = request.form.get("duration_minutes")
    notes = request.form.get("notes", "").strip() or None

    if not subject_id or not duration:
        flash("Please fill in the subject and duration.")
        return redirect(url_for("main.index"))

    try:
        models.create_session(
            user_id=user_id,
            subject_id=int(subject_id),
            duration_minutes=int(duration),
            notes=notes,
        )
    except Exception as e:
        flash(f"Error registering session: {e}")

    return redirect(url_for("main.index"))


@bp.route("/sessions/<int:session_id>/edit", methods=["GET", "POST"])
@login_required
def edit_session(session_id):
    user_id = current_user_id()
    session_obj = models.get_session(user_id, session_id)
    if not session_obj:
        flash("Session not found.")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        duration = request.form.get("duration_minutes")
        notes = request.form.get("notes", "").strip() or None
        if not duration:
            flash("Please enter the duration.")
        else:
            models.update_session(user_id, session_id, int(duration), notes)
            flash("Session updated.")
            return redirect(url_for("main.index"))

    return render_template("edit_session.html", session=session_obj)


@bp.route("/sessions/<int:session_id>/delete", methods=["POST"])
@login_required
def delete_session(session_id):
    user_id = current_user_id()
    if models.delete_session(user_id, session_id):
        flash("Session deleted.")
    else:
        flash("Session not found.")
    return redirect(url_for("main.index"))


# ---------- Reports ----------

@bp.route("/report")
@login_required
def report():
    user_id = current_user_id()
    start = request.args.get("start") or None
    end = request.args.get("end") or None

    report_data = models.report_by_subject(user_id, start, end)
    grand_total = sum(r["total_minutes"] for r in report_data) if report_data else 0

    return render_template(
        "report.html",
        report=report_data,
        grand_total=grand_total,
        start=start,
        end=end,
    )


@bp.route("/report/weekly")
@login_required
def report_weekly():
    user_id = current_user_id()
    data = models.weekly_report(user_id)
    grand_total = sum(r["total_minutes"] for r in data) if data else 0
    return render_template("report_weekly.html", report=data, grand_total=grand_total)


# ---------- CSV export ----------

@bp.route("/export/sessions.csv")
@login_required
def export_sessions_csv():
    user_id = current_user_id()
    start = request.args.get("start") or None
    end = request.args.get("end") or None

    sessions = models.sessions_for_export(user_id, start, end)

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";", lineterminator="\n")
    writer.writerow(["id", "date", "subject", "duration_minutes", "notes"])
    for s in sessions:
        writer.writerow([
            s["id"],
            s["studied_at"],
            s["subject_name"],
            s["duration_minutes"],
            s["notes"] or "",
        ])

    return Response(
        buffer.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=study-sessions.csv"},
    )


# ---------- Authentication ----------

@bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if not username or not password:
            flash("Please fill in username and password.")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.")
        elif password != password2:
            flash("Passwords do not match.")
        elif models.get_user_by_username(username):
            flash("This username is already taken.")
        else:
            try:
                user = models.create_user(username, password)
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                flash("Account created successfully.")
                return redirect(url_for("main.index"))
            except Exception as e:
                flash(f"Error creating account: {e}")

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
            flash(f"Welcome, {user['username']}!")
            return redirect(url_for("main.index"))
        else:
            flash("Incorrect username or password.")

    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("main.login"))