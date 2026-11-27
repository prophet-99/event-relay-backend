from app.db.database import get_database_url


def test_database_url_comes_from_the_environment(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:////app/data/qa.db")

    assert get_database_url() == "sqlite+pysqlite:////app/data/qa.db"
