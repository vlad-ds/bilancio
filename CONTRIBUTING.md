# Contributing to Bilancio

Thank you for your interest in contributing to Bilancio! This document provides guidelines and instructions for contributing.

## Getting Started

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vlad-ds/bilancio.git
   cd bilancio
   ```

2. **Install uv (if not already installed):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create and activate a virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install the package in development mode:**
   ```bash
   uv pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=bilancio --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_balances.py -v
```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Write docstrings for public functions and classes
- Keep functions focused and single-purpose

### Project Structure

```
bilancio/
├── src/bilancio/
│   ├── core/           # Core data structures and utilities
│   ├── domain/         # Domain models (agents, instruments)
│   ├── ops/            # Operations on domain objects
│   ├── engines/        # Computation engines
│   ├── analysis/       # Analysis & analytics tools
│   ├── config/         # Configuration and scenario loading
│   ├── dealer/         # Dealer pricing and trading logic
│   └── ui/             # CLI and visualization
├── tests/              # Test suites
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── examples/           # Example scenarios and notebooks
└── docs/               # Documentation
```

## Submitting Changes

### Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure tests pass:
   ```bash
   uv run pytest tests/ -v
   ```

3. **Commit with clear messages:**
   ```bash
   git commit -m "feat: add new feature description"
   ```

4. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Guidelines

Use conventional commit format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions or modifications
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### What to Include in a PR

- Clear description of changes
- Test coverage for new functionality
- Updated documentation if applicable
- Reference to related issues (if any)

## Reporting Issues

When reporting issues, please include:

1. **Description** of the problem
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Environment details** (Python version, OS, etc.)
6. **Relevant code or error messages**

## Architecture Guidelines

### Double-Entry Invariants

Bilancio enforces strict double-entry bookkeeping. All financial instruments must:
- Have exactly one asset holder and one liability issuer
- Balance at the system level (total assets = total liabilities)

### Agent Types

When adding new agent types:
- Inherit from the base `Agent` class
- Register in `bilancio/domain/agents/__init__.py`
- Update `PolicyEngine` if new holding/issuing rules needed
- Add tests for agent-specific behavior

### Instrument Types

When adding new instruments:
- Inherit from the base `Instrument` class
- Implement `validate_type_invariants()` method
- Register in appropriate module under `bilancio/domain/instruments/`
- Update policy rules if needed

## Questions?

If you have questions about contributing, please open an issue with the "question" label.

Thank you for contributing to Bilancio!
