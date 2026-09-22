"""Architecture boundary tests."""

from __future__ import annotations

import ast
from pathlib import Path


def test_core_modules_do_not_import_pygame() -> None:
    core_directory = Path(__file__).parents[1] / "src" / "simu_monde" / "core"

    for module_path in core_directory.rglob("*.py"):
        module_tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(module_tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        assert "pygame" not in imported_roots, module_path
