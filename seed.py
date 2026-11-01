"""Popula o banco com dados de exemplo para demonstração.

Uso:
    python seed.py

Cria o usuário 'demo' (senha 'demo1234') com 5 matérias e 12 sessões
distribuídas pelas últimas 4 semanas. Se o usuário 'demo' já existir,
os dados antigos dele são apagados antes de recriar.
"""

from datetime import datetime, timedelta

from app import models
from app.database import get_connection, init_db


def main() -> None:
    init_db()

    # Apaga dados anteriores do 'demo' (não afeta outros usuários)
    if models.get_user_by_username("demo"):
        with get_connection() as conn:
            conn.execute("DELETE FROM users WHERE username = 'demo'")
            conn.commit()
        print("Dados anteriores de 'demo' apagados.")

    user = models.create_user("demo", "demo1234")
    user_id = user["id"]
    print(f"Usuário 'demo' criado (id={user_id}).")

    subjects_data = [
        "Cálculo I",
        "Estrutura de Dados",
        "Engenharia de Software",
        "Banco de Dados",
        "Física I",
    ]
    subjects = {}
    for name in subjects_data:
        s = models.create_subject(user_id, name)
        subjects[name] = s["id"]
    print(f"{len(subjects)} matérias criadas.")

    # (dias_atras, matéria, duração, observação)
    sessions_data = [
        (21, "Cálculo I", 60, "Revisão de limites e derivadas"),
        (18, "Estrutura de Dados", 90, "Implementação de lista encadeada"),
        (16, "Engenharia de Software", 45, "Leitura do cap. 3 — metodologias ágeis"),
        (14, "Banco de Dados", 60, "Modelagem ER do projeto final"),
        (12, "Cálculo I", 90, "Resolução de exercícios — integrais"),
        (10, "Física I", 30, "Lista de exercícios — cinemática"),
        (8, "Estrutura de Dados", 75, "Árvores binárias de busca"),
        (6, "Engenharia de Software", 60, "Revisão de requisitos do projeto"),
        (5, "Banco de Dados", 45, "Normalização — 1FN, 2FN, 3FN"),
        (3, "Cálculo I", 60, "Estudo para a P1"),
        (2, "Física I", 45, "Revisão de vetores"),
        (1, "Estrutura de Dados", 90, "Algoritmos de ordenação"),
    ]

    now = datetime.now()
    for days_ago, subject_name, duration, notes in sessions_data:
        studied_at = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO study_sessions "
                "(user_id, subject_id, duration_minutes, studied_at, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, subjects[subject_name], duration, studied_at, notes),
            )
            conn.commit()

    total = sum(s[2] for s in sessions_data)
    print(f"{len(sessions_data)} sessões criadas.")
    print(f"Total: {total} minutos ({total/60:.1f} horas).")
    print("Pronto! Faça login com 'demo' / 'demo1234'.")


if __name__ == "__main__":
    main()