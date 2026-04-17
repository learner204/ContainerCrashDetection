from pathlib import Path


def test_all_python_files_are_syntax_valid():
    root = Path(__file__).resolve().parents[1]
    python_files = [
        p for p in root.rglob("*.py")
        if ".venv" not in p.parts and "__pycache__" not in p.parts
    ]

    assert python_files, "No Python files found in the repository"

    for file_path in python_files:
        source = file_path.read_text(encoding="utf-8")
        compile(source, str(file_path), "exec")


def test_repo_entrypoints_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "app.py").exists()
    assert (root / "main.py").exists()
