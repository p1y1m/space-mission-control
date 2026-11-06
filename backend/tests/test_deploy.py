from app import deploy


def test_deploy_runs_migrations_before_seeding(monkeypatch):
    events = []

    class DatabaseContext:
        def __enter__(self):
            events.append("open")
            return "database-session"

        def __exit__(self, *_):
            events.append("close")

    monkeypatch.setattr(deploy.command, "upgrade", lambda config, revision: events.append(revision))
    monkeypatch.setattr(deploy, "SessionLocal", DatabaseContext)
    monkeypatch.setattr(deploy, "seed_satellites", lambda db: events.append(f"seed:{db}"))

    deploy.main()

    assert events == ["head", "open", "seed:database-session", "close"]
