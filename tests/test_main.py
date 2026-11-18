import pytest

from src.main import create_app


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setenv("CLIENT_ID", "test-client")
    monkeypatch.setenv("CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("REDIRECT_URI", "http://localhost/callback")
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URI", f"sqlite:///{tmp_path / 'whoops.db'}")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")

    application = create_app()
    yield application
    application.config["Scheduler"].shutdown(wait=False)


def test_app_starts_and_serves_index(app):
    response = app.test_client().get("/")

    assert response.status_code == 200
