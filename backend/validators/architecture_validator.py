"""Static architecture validator for Synapse CI guardrails."""

import ast
from pathlib import Path
from typing import List


def get_imports(filepath: Path) -> List[str]:
    """Parses a Python file and returns a list of imported modules."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))
    except Exception:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def check_specialists(backend_dir: Path, errors: List[str]) -> None:
    agents_dir = backend_dir / "agents"
    if not agents_dir.exists():
        return
    for file in agents_dir.glob("*.py"):
        if file.name in ("__init__.py", "base.py", "live_base.py"):
            continue
        imports = get_imports(file)
        for imp in imports:
            if imp.startswith("agents.") and imp not in (
                "agents.base",
                "agents.live_base",
            ):
                errors.append(
                    f"Architectural Violation: {file.name} imports another specialist ({imp})"
                )


def check_infrastructure(backend_dir: Path, errors: List[str]) -> None:
    infrastructure_dirs = [
        "services",
        "core",
        "observability",
        "registry",
        "cache",
        "config",
    ]
    for d in infrastructure_dirs:
        infra_dir = backend_dir / d
        if not infra_dir.exists():
            continue
        for file in infra_dir.rglob("*.py"):
            imports = get_imports(file)
            for imp in imports:
                if (
                    imp.startswith("agents.")
                    and imp not in ("agents.base", "agents.live_base")
                    and d != "registry"
                ):
                    errors.append(
                        f"Architectural Violation: Infrastructure ({file.name}) imports specialist ({imp})"
                    )


def check_tick_context(backend_dir: Path, errors: List[str]) -> None:
    tick_context_file = backend_dir / "core" / "tick_context.py"
    if not tick_context_file.exists():
        return
    with open(tick_context_file, "r", encoding="utf-8") as f:
        content = f.read()
        if "def __setattr__" in content or "self.evidence_delta =" in content:
            if (
                "frozen=True" not in content
                and "@dataclass(frozen=True)" not in content
            ):
                errors.append(
                    "Architectural Violation: TickContext must be immutable (frozen=True)"
                )


def validate_architecture(backend_dir: Path) -> bool:
    """Validates structural guardrails."""
    errors: List[str] = []
    check_specialists(backend_dir, errors)
    check_infrastructure(backend_dir, errors)
    check_tick_context(backend_dir, errors)

    if errors:
        for err in errors:
            print(err)
        return False

    print("Architecture validation passed successfully.")
    return True


if __name__ == "__main__":
    backend_path = Path(__file__).parent.parent
    if not validate_architecture(backend_path):
        exit(1)
    exit(0)
