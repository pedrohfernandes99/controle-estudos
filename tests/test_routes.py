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