def test_index_sem_dados(client):
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Nenhuma matéria cadastrada ainda" in html


def test_add_subject_pela_rota(client):
    response = client.post(
        "/subjects",
        data={"name": "Cálculo I"},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Cálculo I" in html


def test_add_subject_nome_vazio(client):
    response = client.post(
        "/subjects",
        data={"name": "   "},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert "não pode ser vazio" in html


def test_add_duplicate_subject_mostra_erro(client):
    client.post("/subjects", data={"name": "Cálculo I"})
    response = client.post(
        "/subjects",
        data={"name": "Cálculo I"},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert "já existe" in html


def test_add_session_pela_rota(client):
    client.post("/subjects", data={"name": "Cálculo I"})
    response = client.post(
        "/sessions",
        data={"subject_id": "1", "duration_minutes": "60", "notes": "Revisão"},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Cálculo I" in html
    assert "60 min" in html


def test_edit_subject_get(client):
    client.post("/subjects", data={"name": "Cálculo I"})
    response = client.get("/subjects/1/edit")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Cálculo I" in html


def test_edit_subject_post(client):
    client.post("/subjects", data={"name": "Cálculo I"})
    response = client.post(
        "/subjects/1/edit",
        data={"name": "Cálculo II"},
        follow_redirects=True,
    )
    html = response.data.decode("utf-8")
    assert "Cálculo II" in html


def test_delete_subject(client):
    client.post("/subjects", data={"name": "Cálculo I"})
    response = client.post("/subjects/1/delete", follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "Matéria apagada" in html
    assert "Nenhuma matéria cadastrada ainda" in html


def test_edit_session_get(client):
    client.post("/subjects", data={"name": "Cálculo I"})
    client.post(
        "/sessions",
        data={"subject_id": "1", "duration_minutes": "60", "notes": ""},
    )
    response = client.get("/sessions/1/edit")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "60" in html


def test_report_vazio(client):
    response = client.get("/report")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Nenhuma sessão registrada ainda" in html


def test_report_com_sessao(client):
    client.post("/subjects", data={"name": "Cálculo I"})
    client.post(
        "/sessions",
        data={"subject_id": "1", "duration_minutes": "90"},
    )
    response = client.get("/report")
    html = response.data.decode("utf-8")
    assert "Cálculo I" in html
    assert "90" in html

    
def test_report_com_filtro_por_periodo(client):
    client.post("/subjects", data={"name": "Cálculo I"})
    client.post(
        "/sessions",
        data={"subject_id": "1", "duration_minutes": "60"},
    )

    # Insere manualmente uma sessão antiga (janeiro de 2026)
    from app.database import get_connection
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO study_sessions (subject_id, duration_minutes, studied_at) "
            "VALUES (?, ?, ?)",
            (1, 30, "2026-01-15 10:00:00"),
        )
        conn.commit()

    # Filtro pelo período de janeiro: só a sessão de 30 min aparece
    response = client.get("/report?start=2026-01-01&end=2026-01-31")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "30 min" in html
    assert "60 min" not in html


def test_report_filtro_sem_resultados(client):
    client.post("/subjects", data={"name": "Cálculo I"})
    client.post(
        "/sessions",
        data={"subject_id": "1", "duration_minutes": "60"},
    )

    # Filtro em um período do futuro: nenhuma sessão
    response = client.get("/report?start=2099-01-01&end=2099-12-31")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Nenhuma sessão registrada no período selecionado" in html