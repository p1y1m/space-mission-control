import json
import tomllib
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_vercel_configuration_targets_fastapi_entrypoint():
    vercel = json.loads((BACKEND_ROOT / "vercel.json").read_text())
    pyproject = tomllib.loads((BACKEND_ROOT / "pyproject.toml").read_text())

    assert vercel["framework"] == "fastapi"
    assert "app/main.py" in vercel["functions"]
    assert pyproject["tool"]["vercel"]["entrypoint"] == "app.main:app"
    assert pyproject["tool"]["vercel"]["scripts"]["build"] == "python -m app.deploy"
    assert (BACKEND_ROOT / "requirements.txt").is_file()
    assert (BACKEND_ROOT / ".python-version").read_text().strip() == "3.12"
