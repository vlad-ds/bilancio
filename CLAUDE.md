- Use implementation subagents (in parallel) to execute code changes whenever possible, but always review what the subagents wrote, find possible issues, and fix them if necessary.
- Always use `uv run` instead of `python` to run Python commands in this project
- Remove all temporary test_ files when they're no longer needed
- Store temporary test files in a gitignored temp/ folder instead of the project root

## Running Tests
- Run all tests: `uv run pytest tests/ -v`
- Run with coverage: `uv run pytest tests/ --cov=bilancio --cov-report=term-missing`
- Run specific test file: `uv run pytest tests/unit/test_balances.py -v`
- Tests use pytest, installed via: `uv add pytest pytest-cov --dev`

## Jupyter Notebooks
- **ALWAYS TEST NOTEBOOKS BEFORE PRESENTING**: Run code snippets iteratively to catch errors
- Test each cell's code with `uv run python -c "..."` before including in notebook
- Only present notebooks after verifying no errors occur
- To open notebooks in browser: `uv run jupyter notebook <path>` (runs in background)
- Common pitfalls in bilancio:
  - Must use actual agent classes (Bank, Household, Firm) not Agent(kind="bank") - policy checks isinstance()
  - Check function signatures - parameter order matters
  - Verify all imports work before creating notebook

### Balance Sheet Display
- **Use existing display functions** - Always use `bilancio.analysis.visualization.display_agent_balance_table()` and `display_multiple_agent_balances()` instead of creating custom display functions
- **Prefer 'rich' format** - Use `format='rich'` for pretty formatted output (default). This gives nicely formatted tables with colors and borders
- **Use 'simple' format only when needed** - Use `format='simple'` only when balance sheets have many items that would be cramped in the rich format (simple format has more room)
- **Get balance data with agent_balance()** - Use `bilancio.analysis.balances.agent_balance()` to get structured balance sheet data for analysis

### Testing Notebooks - Critical Lessons
- **ALWAYS TEST AFTER ANY CHANGE** - Every time you touch/edit/modify a notebook, you MUST run the complete testing from scratch using `uv run jupyter nbconvert --execute <notebook.ipynb>`. NO EXCEPTIONS.
- **Always test notebooks by executing them directly** - Use `uv run jupyter nbconvert --execute <notebook.ipynb>` to run the actual notebook. Don't extract code to test in separate Python files.
- **Check the ENTIRE output of every cell** - Not just whether it executes without errors, but what each cell actually produces. A notebook can "run" without errors but still produce incorrect results.
- **Read actual outputs, not just success messages** - A notebook can execute "successfully" (no exceptions) but still produce wrong results. Must examine the actual output values.
- **When notebooks don't work as expected** - The issue might not be in the notebook itself but in the underlying code it's calling (check the actual library functions being used).
- **For complex debugging**:
  - First, check if the notebook executes at all
  - Then, examine output of each cell systematically
  - Trace through the logic to find where results diverge from expectations
  - Test individual functions separately only AFTER identifying where the problem occurs
- **When editing notebooks is problematic** - Sometimes it's better to recreate from scratch than to fix complex editing issues with notebook cells

### Creating Notebooks - Essential Rules
- **Ensure correct cell types** - Double-check that code cells are type "code" and markdown cells are type "markdown". Mixed up cell types cause confusing errors.
- **Add sufficient output for debugging** - Every cell should produce enough output to understand what's happening:
  - Print intermediate results and state changes
  - Show balance sheets after each operation
  - Log events and settlements as they occur
  - Display verification checks with actual vs expected values
  - Include descriptive messages explaining what each step does
- **Make notebooks self-documenting** - The output should tell a clear story of what's happening without needing to read the code
- When I tell you to implement a plan from @docs/plans/, always make sure you start from main with clean git status - if not, stop and tell me. Then, create a new branch with the name of the plan and start work.

## UI/Rendering Work
- **ALWAYS TEST HTML OUTPUT**: When making any changes to rendering/UI/display code:
  1. Rebuild the HTML after each change: `uv run bilancio run examples/scenarios/simple_bank.yaml --max-days 3 --html temp/demo.html`
  2. Open it directly in the browser: `open temp/demo.html`
  3. Provide the user with the CLI command to run in their terminal for testing
- **VERIFY COMPLETENESS**: After generating HTML:
  1. Read the source YAML file to understand what should be displayed
  2. Read the generated HTML file to check all information is present
  3. Ensure ALL events are displayed (setup events, payable creation, phase events, etc.)
  4. Verify agent list is shown at the top
  5. Think carefully about what might be missing
- **Verify visual output**: Read the generated HTML file to ensure events, tables, and formatting display correctly
- **Test with real scenarios**: Use actual scenario files to test rendering changes, not just unit tests