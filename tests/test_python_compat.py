from __future__ import annotations

import ast
from pathlib import Path


def test_project_python_sources_parse_as_python_310() -> None:
    """The canonical OptiPlex runtime is Python 3.10; reject newer-only syntax."""
    root = Path(__file__).resolve().parents[1]
    sources = sorted(
        p for p in root.rglob("*.py")
        if ".git" not in p.parts and "__pycache__" not in p.parts and ".venv" not in p.parts
    )
    assert sources
    failures: list[str] = []
    for path in sources:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3, 10))
        except SyntaxError as exc:
            failures.append(f"{path.relative_to(root)}:{exc.lineno}: {exc.msg}")
    assert not failures, "Python 3.10 syntax compatibility failures:\n" + "\n".join(failures)
