# core_tools
Python utilities for logging, file management, and object formatting.

## Installation

Install the package from the repository root:

```bash
python -m pip install .
```

For development, prefer an editable install:

```bash
python -m pip install -e .
```

## Package Layout

The library now uses a modern `src` layout so pip installs package only the supported import surface:

```text
src/core_tools/
```

Import from the package namespace:

```python
from core_tools.logger import create_logger
```

Legacy top-level module files remain as compatibility shims for local consumers, but new code should import from `core_tools`.

## API Style

New code should use snake_case helpers. Legacy camelCase helpers are still available as compatibility aliases.

Examples:

```python
from core_tools.file_management import get_json_dict, update_json_file
from core_tools.object_management import string_formatter, large_sentence_display
```

## Releases

This project follows semantic versioning.

Build distribution artifacts:

```bash
python -m pip install -e .[dev]
python -m build
```

Validate artifacts:

```bash
python -m twine check dist/*
```

Upload to PyPI:

```bash
python -m twine upload dist/*
```

Before each release, update the package version in `pyproject.toml` and `src/core_tools/__init__.py`, then add release notes to `CHANGELOG.md`.

### GitHub Actions Publish Flow

This repository includes a publish workflow at `.github/workflows/publish.yml`.

What it does:
- Builds sdist and wheel
- Runs metadata validation with `twine check`
- Publishes to PyPI on GitHub Release publish
- Supports manual publish to TestPyPI via `workflow_dispatch`
- Disables release attestations for now, which avoids the transparency-log upload path that was failing

Setup required once:
1. In PyPI, create a Trusted Publisher for this project:
	- Owner: `crystalpoplar`
	- Repository: `core_tools`
	- Workflow: `publish.yml`
	- Environment: `pypi`
2. In TestPyPI, create the same Trusted Publisher with environment `testpypi`.
3. In GitHub repo settings, create environments named `pypi` and `testpypi`.

Release usage:
1. Bump version in `pyproject.toml` and `src/core_tools/__init__.py`.
2. Commit and push to `main`.
3. Create and publish a GitHub Release (for example `v0.1.1`).
4. Workflow publishes package to PyPI automatically.



