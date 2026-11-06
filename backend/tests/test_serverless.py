from fastapi.testclient import TestClient

import app.main as main


def test_serverless_lifespan_does_not_initialize_database(monkeypatch):
    monkeypatch.setattr(main.settings, "vercel", "1")

    def fail_if_called(*_, **__):
        raise AssertionError("schema initialization ran during a serverless cold start")

    monkeypatch.setattr(main.Base.metadata, "create_all", fail_if_called)
    with TestClient(main.app):
        pass
