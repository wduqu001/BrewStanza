# Contributing to BrewStanza

First off, thank you for considering contributing to BrewStanza! It's people like you that make BrewStanza a great tool for everyone.

## Local Development Setup

BrewStanza is built with Python 3.11+.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wduqu001/BrewStanza.git
   cd BrewStanza
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Development Workflow

### Coding Standards
We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting, and [Mypy](https://github.com/python/mypy) for type checking.

Run the quality gates before committing:
```bash
# Lint and format
ruff check src/
ruff format src/

# Type check
mypy src/
```

### Running Tests
We use [pytest](https://docs.pytest.org/) for testing with [pytest-cov](https://github.com/pytest-dev/pytest-cov) for coverage.

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=brewstanza --cov-report=term-missing
```

We aim for **>80% coverage** on all new features.

## Submitting Changes

1. Create a new branch for your feature or bugfix: `git checkout -b feature/my-new-feature`.
2. Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/).
3. Push to your fork and submit a pull request.

Please ensure all quality gates pass before submitting.

## Reporting Issues
Use the GitHub issue tracker to report bugs or suggest features. Please include:
- Your macOS version.
- Steps to reproduce the bug.
- Expected vs. actual behavior.

## License
By contributing, you agree that your contributions will be licensed under its MIT License.
