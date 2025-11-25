#!/usr/bin/env python3
"""
Assemble all dealer ring examples into a single text file for verification.

This script:
1. Creates a tree structure of all example files
2. Concatenates all Python example files with clear headers
3. Concatenates all HTML report files with clear headers
4. Outputs everything to "worked_examples.txt"

Usage:
    uv run python examples/dealer_ring/assemble_examples.py
"""

import os
from pathlib import Path


def get_file_tree(directory: Path, prefix: str = "") -> str:
    """Generate a text tree representation of the directory."""
    lines = []
    items = sorted(directory.iterdir())

    # Separate files and directories
    dirs = [d for d in items if d.is_dir() and not d.name.startswith('.')]
    files = [f for f in items if f.is_file() and not f.name.startswith('.')]

    for i, item in enumerate(dirs + files):
        is_last = (i == len(dirs) + len(files) - 1)
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{item.name}")

        if item.is_dir():
            extension = "    " if is_last else "│   "
            lines.append(get_file_tree(item, prefix + extension))

    return "\n".join(filter(None, lines))


def main():
    base_dir = Path(__file__).parent
    out_dir = base_dir / "out"
    output_file = base_dir / "worked_examples.txt"

    sections = []

    # Header
    sections.append("=" * 80)
    sections.append("DEALER RING WORKED EXAMPLES")
    sections.append("=" * 80)
    sections.append("")
    sections.append("This file contains all dealer ring example implementations and their")
    sections.append("corresponding HTML reports for verification against the specification.")
    sections.append("")
    sections.append("Specification PDF: docs/dealer_ring/dealer_examples.pdf")
    sections.append("")

    # File tree
    sections.append("-" * 80)
    sections.append("FILE STRUCTURE")
    sections.append("-" * 80)
    sections.append("")
    sections.append("examples/dealer_ring/")
    sections.append(get_file_tree(base_dir))
    sections.append("")

    # Example-to-PDF mapping
    sections.append("-" * 80)
    sections.append("EXAMPLE TO PDF SECTION MAPPING")
    sections.append("-" * 80)
    sections.append("")
    mapping = [
        ("Example 1", "PDF Section 2", "Selling a Migrating Claim"),
        ("Example 2", "PDF Section 3", "Maturing Debt and Cross-Bucket Reallocation"),
        ("Example 3", "PDF Section 4", "Outside-Bid Clipping Toggle"),
        ("Example 4", "PDF Section 5", "Dealer Reaches Inventory Limit and VBT Layoff"),
        ("Example 5", "PDF Section 6", "Dealer Earns Over Time"),
        ("Example 6", "PDF Section 7", "Bid-Side Pass-Through"),
        ("Example 7", "PDF Section 8", "Edge Rung Without Interior Clipping"),
        ("Example 8", "PDF Section 9", "Guard at Very Low Mid M"),
        ("Example 9", "PDF Section 10", "Partial-Recovery Default (R=0.375)"),
        ("Example 10", "PDF Section 11", "Trader-Held Rebucketing"),
        ("Example 11", "PDF Section 12", "Partial-Recovery Default (R=0.6)"),
        ("Example 12", "PDF Section 13", "Capacity Integer Crossing"),
        ("Example 13", "PDF Section 14", "Minimal Event-Loop Harness"),
        ("Example 14", "PDF Section 15", "Ticket-Level Transfer"),
    ]
    for ex, pdf, title in mapping:
        sections.append(f"  {ex:12s} -> {pdf:14s} : {title}")
    sections.append("")

    # Python files
    sections.append("=" * 80)
    sections.append("PYTHON SOURCE FILES")
    sections.append("=" * 80)
    sections.append("")

    # Sort by example number numerically
    def get_example_num(path: Path) -> int:
        name = path.stem  # e.g., "example10_trader_rebucket"
        num_str = name.split("_")[0].replace("example", "")
        return int(num_str) if num_str.isdigit() else 999

    py_files = sorted(base_dir.glob("example*_*.py"), key=get_example_num)
    for py_file in py_files:
        sections.append("#" * 80)
        sections.append(f"# FILE: {py_file.name}")
        sections.append(f"# PATH: examples/dealer_ring/{py_file.name}")
        sections.append("#" * 80)
        sections.append("")
        sections.append(py_file.read_text())
        sections.append("")
        sections.append("")

    # HTML files
    sections.append("=" * 80)
    sections.append("HTML REPORT FILES")
    sections.append("=" * 80)
    sections.append("")

    if out_dir.exists():
        def get_html_example_num(path: Path) -> int:
            name = path.stem  # e.g., "example10_report"
            num_str = name.split("_")[0].replace("example", "")
            return int(num_str) if num_str.isdigit() else 999

        html_files = sorted(out_dir.glob("example*_report.html"), key=get_html_example_num)
        for html_file in html_files:
            sections.append("#" * 80)
            sections.append(f"# FILE: {html_file.name}")
            sections.append(f"# PATH: examples/dealer_ring/out/{html_file.name}")
            sections.append("#" * 80)
            sections.append("")
            try:
                sections.append(html_file.read_text())
            except Exception as e:
                sections.append(f"[Error reading file: {e}]")
            sections.append("")
            sections.append("")
    else:
        sections.append("No HTML reports found. Run the examples first to generate them.")
        sections.append("")

    # Write output
    output_text = "\n".join(sections)
    output_file.write_text(output_text)

    print(f"Assembled {len(py_files)} Python files")
    print(f"Assembled {len(list(out_dir.glob('example*_report.html'))) if out_dir.exists() else 0} HTML files")
    print(f"Output written to: {output_file}")
    print(f"Total size: {len(output_text):,} characters")


if __name__ == "__main__":
    main()
