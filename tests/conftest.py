import pytest

import run as app_module
from app import database, models
from app.database import init_db


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Cria um banco de dados temporário e isolado para o teste."""
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    init_db()
    yield


@pytest.fixture
def user(db):
    """Cria e devolve o usuário padrão 'testuser' (senha 'senha123')."""
    return models.create_user("testuser", "senha123")


@pytest.fixture
def client(db):
    """Cliente de teste do Flask (anônimo, sem login)."""
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


@pytest.fixture
def auth_client(client, user):
    """Cliente já autenticado como 'testuser'."""
    client.post(
        "/login",
        data={"username": "testuser", "password": "senha123"},
    )
    return client