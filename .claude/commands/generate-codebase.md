---
allowed-tools: Bash
description: Generate the codebase markdown file and open in Finder
---

Run the codebase markdown generation script and open the project folder in Finder:

1. Execute: `uv run python scripts/generate_codebase_markdown.py`
2. Open the project folder in Finder to view the generated `codebase_for_llm.md` file
3. Report the stats (number of source files, test files, and output file size)

This will create a comprehensive markdown file containing all source code that can be shared with LLMs for analysis.