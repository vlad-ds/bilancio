# Installation

## Requirements

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/vlad-ds/bilancio.git
cd bilancio
```

2. Create and activate a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package in development mode:
```bash
uv pip install -e ".[dev]"
```

## Running Tests

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=bilancio --cov-report=term-missing
```
