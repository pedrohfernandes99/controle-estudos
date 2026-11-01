from functools import wraps

from flask import session, redirect, url_for, flash


def login_required(view):
    """Redireciona para /login se o usuário não estiver autenticado."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):         
            flash("Please log in to continue.")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


def current_user_id() -> int:
    """Devolve o id do usuário logado. Use apenas dentro de rotas protegidas."""
    return session["user_id"]