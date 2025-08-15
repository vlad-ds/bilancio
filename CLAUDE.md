- Use implementation subagents (in parallel) to execute do code changes whenever possible.
- Always use `uv run` instead of `python` to run Python commands in this project

## Running Tests
- Run all tests: `uv run pytest tests/ -v`
- Run with coverage: `uv run pytest tests/ --cov=bilancio --cov-report=term-missing`
- Run specific test file: `uv run pytest tests/unit/test_balances.py -v`
- Tests use pytest, installed via: `uv add pytest pytest-cov --dev`

## Jupyter Notebooks
- **ALWAYS TEST NOTEBOOKS BEFORE PRESENTING**: Run code snippets iteratively to catch errors
- Test each cell's code with `uv run python -c "..."` before including in notebook
- Only present notebooks after verifying no errors occur
- Common pitfalls in bilancio:
  - Must use actual agent classes (Bank, Household) not Agent(kind="bank") - policy checks isinstance()
  - Check function signatures - parameter order matters
  - Verify all imports work before creating notebook