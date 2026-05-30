from __future__ import annotations

from pathlib import Path


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.exists() or candidate.is_absolute():
        return candidate

    app_relative = Path(__file__).resolve().parent.parent / candidate
    if app_relative.exists():
        return app_relative

    return candidate
