"""Architecture boundary tests."""

from __future__ import annotations

import ast
from pathlib import Path


def _imported_modules(module_path: Path) -> set[str]:
    module_tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
    imported_modules: set[str] = set()
    for node in ast.walk(module_tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)
    return imported_modules


def test_core_modules_do_not_import_rendering_or_packaging() -> None:
    core_directory = Path(__file__).parents[1] / "src" / "simu_monde" / "core"
    for module_path in core_directory.rglob("*.py"):
        imported_roots = {module.split(".")[0] for module in _imported_modules(module_path)}
        assert imported_roots.isdisjoint({"pygame", "PyInstaller"}), module_path


def test_vegetation_module_does_not_import_adapters() -> None:
    vegetation_module = Path(__file__).parents[1] / "src" / "simu_monde" / "core" / "vegetation.py"

    assert not any(
        module.startswith("simu_monde.adapters") for module in _imported_modules(vegetation_module)
    )


def test_herbivore_module_does_not_import_adapters() -> None:
    herbivore_module = Path(__file__).parents[1] / "src" / "simu_monde" / "core" / "herbivore.py"

    assert not any(
        module.startswith("simu_monde.adapters") for module in _imported_modules(herbivore_module)
    )


def test_water_module_does_not_import_adapters() -> None:
    water_module = Path(__file__).parents[1] / "src" / "simu_monde" / "core" / "water.py"

    assert not any(
        module.startswith("simu_monde.adapters") for module in _imported_modules(water_module)
    )


def test_homeostasis_module_does_not_import_adapters() -> None:
    module = Path(__file__).parents[1] / "src" / "simu_monde" / "core" / "homeostasis.py"

    assert not any(
        imported.startswith("simu_monde.adapters") for imported in _imported_modules(module)
    )


def test_lifecycle_module_does_not_import_adapters() -> None:
    module = Path(__file__).parents[1] / "src" / "simu_monde" / "core" / "lifecycle.py"

    assert not any(
        imported.startswith("simu_monde.adapters") for imported in _imported_modules(module)
    )
