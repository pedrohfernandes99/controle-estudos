import pytest


# ---------- Rotas protegidas redirecionam para login ----------

@pytest.mark.parametrize("method,path", [
    ("get", "/"),
    ("get", "/report"),
    ("get", "/report/weekly"),
    ("get", "/export/sessions.csv"),
    ("get", "/subjects/1/edit"),
    ("get", "/sessions/1/edit"),
    ("post", "/subjects"),
    ("post", "/sessions"),
    ("post", "/subjects/1/delete"),
    ("post", "/sessions/1/delete"),
])
def test_rotas_protegidas_redirecionam(client, method, path):
    response = getattr(client, method)(path, follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "Faça login para continuar" in html


# ---------- Home ----------

def test_index_sem_dados(auth_client):
    response = auth_client.get("/")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Nenhuma matéria cadastrada ainda" in html


# ---------- Matérias ----------

def test_add_subject_pela_rota(auth_client):
    response = auth_client.post(
        "/subjects",
        data={"name": "Cálculo I"},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Cálculo I" in html


def test_add_subject_nome_vazio(auth_client):
    response = auth_client.post(
        "/subjects",
        data={"name": "   "},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert "não pode ser vazio" in html


def test_add_duplicate_subject_mostra_erro(auth_client):
    auth_client.post("/subjects", data={"name": "Cálculo I"})
    response = auth_client.post(
        "/subjects",
        data={"name": "Cálculo I"},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert "já existe" in html


def test_edit_subject_get(auth_client):
    auth_client.post("/subjects", data={"name": "Cálculo I"})
    response = auth_client.get("/subjects/1/edit")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Cálculo I" in html


def test_edit_subject_post(auth_client):
    auth_client.post("/subjects", data={"name": "Cálculo I"})
    response = auth_client.post(
        "/subjects/1/edit",
        data={"name": "Cálculo II"},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert "Cálculo II" in html


def test_delete_subject(auth_client):
    auth_client.post("/subjects", data={"name": "Cálculo I"})
    response = auth_client.post("/subjects/1/delete", follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "Matéria apagada" in html
    assert "Nenhuma matéria cadastrada ainda" in html


# ---------- Sessões ----------

def test_add_session_pela_rota(auth_client):
    auth_client.post("/subjects", data={"name": "Cálculo I"})
    response = auth_client.post(
        "/sessions",
        data={"subject_id": "1", "duration_minutes": "60", "notes": "Revisão"},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Cálculo I" in html
    assert "60 min" in html


def test_edit_session_get(auth_client):
    auth_client.post("/subjects", data={"name": "Cálculo I"})
    auth_client.post(
        "/sessions",
        data={"subject_id": "1", "duration_minutes": "60", "notes": ""},
    )
    response = auth_client.get("/sessions/1/edit")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "60" in html


# ---------- Relatórios ----------

def test_report_vazio(auth_client):
    response = auth_client.get("/report")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Nenhuma sessão registrada ainda" in html


def test_report_com_sessao(auth_client):
    auth_client.post("/subjects", data={"name": "Cálculo I"})
    auth_client.post(
        "/sessions",
        data={"subject_id": "1", "duration_minutes": "90"},
    )
    response = auth_client.get("/report")
    html = response.data.decode("utf-8")
    assert "Cálculo I" in html
    assert "90" in html


def test_report_com_filtro_por_periodo(auth_client, user):
    auth_client.post("/subjects", data={"name": "Cálculo I"})
    auth_client.post(
        "/sessions",
        data={"subject_id": "1", "duration_minutes": "60"},
    )

    from app.database import get_connection
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO study_sessions (user_id, subject_id, duration_minutes, studied_at) "
            "VALUES (?, ?, ?, ?)",
            (user["id"], 1, 30, "2026-01-15 10:00:00"),
        )
        conn.commit()

    response = auth_client.get("/report?start=2026-01-01&end=2026-01-31")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "30 min" in html
    assert "60 min" not in html


def test_report_filtro_sem_resultados(auth_client):
    auth_client.post("/subjects", data={"name": "Cálculo I"})
    auth_client.post(
        "/sessions",
        data={"subject_id": "1", "duration_minutes": "60"},
    )
    response = auth_client.get("/report?start=2099-01-01&end=2099-12-31")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Nenhuma sessão registrada no período selecionado" in html


# ---------- Exportação CSV ----------

def test_export_csv_sem_dados(auth_client):
    response = auth_client.get("/export/sessions.csv")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    body = response.data.decode("utf-8")
    assert "id;data;materia;duracao_minutos;observacoes" in body


def test_export_csv_com_dados(auth_client):
    auth_client.post("/subjects", data={"name": "Cálculo I"})
    auth_client.post(
        "/sessions",
        data={"subject_id": "1", "duration_minutes": "60", "notes": "Revisão"},
    )
    response = auth_client.get("/export/sessions.csv")
    assert response.status_code == 200
    assert "attachment" in response.headers["Content-Disposition"]
    assert "estudos.csv" in response.headers["Content-Disposition"]
    body = response.data.decode("utf-8")
    assert "Cálculo I" in body
    assert "60" in body
    assert "Revisão" in body


# ---------- Isolamento entre usuários ----------

def test_usuario_nao_ve_materia_de_outro(auth_client):
    from app import models
    other = models.create_user("outro", "senha123")
    models.create_subject(other["id"], "Matéria Secreta")

    response = auth_client.get("/")
    html = response.data.decode("utf-8")
    assert "Matéria Secreta" not in html


def test_usuario_nao_consegue_editar_materia_de_outro(auth_client):
    from app import models
    other = models.create_user("outro", "senha123")
    subject = models.create_subject(other["id"], "Matéria Secreta")

    response = auth_client.get(
        f"/subjects/{subject['id']}/edit",
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert "Matéria não encontrada" in html


# ---------- Autenticação ----------

def test_register_cria_usuario_e_loga(client):
    response = client.post(
        "/register",
        data={"username": "pedro", "password": "senha123", "password2": "senha123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Conta criada com sucesso" in html
    assert "pedro" in html

    with client.session_transaction() as sess:
        assert sess["username"] == "pedro"


def test_register_senhas_diferentes(client):
    response = client.post(
        "/register",
        data={"username": "pedro", "password": "senha123", "password2": "outra123"},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert "As senhas não conferem" in html

    from app import models
    assert models.get_user_by_username("pedro") is None


def test_login_correto(client):
    from app import models
    models.create_user("pedro", "senha123")

    response = client.post(
        "/login",
        data={"username": "pedro", "password": "senha123"},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert "Bem-vindo, pedro" in html

    with client.session_transaction() as sess:
        assert sess["username"] == "pedro"


def test_login_senha_errada(client):
    from app import models
    models.create_user("pedro", "senha123")

    response = client.post(
        "/login",
        data={"username": "pedro", "password": "errada"},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert "Usuário ou senha incorretos" in html

    with client.session_transaction() as sess:
        assert "username" not in sess


def test_logout(client):
    from app import models
    models.create_user("pedro", "senha123")

    client.post("/login", data={"username": "pedro", "password": "senha123"})
    response = client.post("/logout", follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "Você saiu" in html

    with client.session_transaction() as sess:
        assert "username" not in sess