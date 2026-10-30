import pytest

import run as app_module
from app import database
from app.database import init_db


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Cria um banco de dados temporário e isolado para o teste."""
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    init_db()
    yield


@pytest.fixture
def client(db):
    """Cria um cliente de teste do Flask (simula o navegador)."""
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c