#!/usr/bin/env python3
"""
Generate a markdown file containing the codebase structure and content for LLM ingestion.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Set


def get_tree_output(path: str, exclude_patterns: List[str] = None) -> str:
    """Generate tree output for a given path."""
    exclude_args = []
    if exclude_patterns:
        for pattern in exclude_patterns:
            exclude_args.extend(['-I', pattern])
    
    try:
        cmd = ['tree', path, '-a'] + exclude_args
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        # Fallback if tree command is not available
        return generate_simple_tree(path, exclude_patterns or [])


def generate_simple_tree(path: str, exclude_patterns: List[str]) -> str:
    """Generate a simple tree structure if tree command is not available."""
    def should_exclude(name: str) -> bool:
        exclude_list = [
            '__pycache__', '.pyc', '.git', '.pytest_cache', '.coverage', 
            'egg-info', '.conductor', '.uv', 'node_modules', '.DS_Store',
            '.mypy_cache', '.ruff_cache', 'htmlcov', '.tox', '.nox',
            '.hypothesis', '.env', '.venv', 'venv', 'env', '.idea',
            '.vscode', '.claude', '*.lock', '.ipynb_checkpoints'
        ]
        return any(exc in name for exc in exclude_list)
    
    def walk_dir(dir_path: Path, prefix: str = "") -> List[str]:
        lines = []
        items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        
        for i, item in enumerate(items):
            if should_exclude(item.name):
                continue
                
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            lines.append(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir():
                extension = "    " if is_last else "│   "
                lines.extend(walk_dir(item, prefix + extension))
        
        return lines
    
    lines = [str(path)]
    lines.extend(walk_dir(Path(path)))
    return "\n".join(lines)


def get_python_files(directory: Path) -> List[Path]:
    """Get all Python files in a directory recursively."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return sorted(python_files)


def get_git_history() -> str:
    """Get the full git commit history."""
    try:
        # Get detailed git log with full commit messages
        cmd = ['git', 'log', '--pretty=format:%H|%ai|%an|%s%n%b', '--reverse']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        commits = []
        current_commit = []
        
        for line in result.stdout.split('\n'):
            if '|' in line and len(line.split('|')) >= 4:
                # This is a new commit header
                if current_commit:
                    # Process previous commit
                    parts = current_commit[0].split('|', 3)
                    if len(parts) == 4:
                        commit_hash, date, author, subject = parts
                        body = '\n'.join(current_commit[1:]) if len(current_commit) > 1 else ""
                        commits.append({
                            'hash': commit_hash[:8],
                            'date': date.split(' ')[0],  # Just the date part
                            'author': author,
                            'subject': subject,
                            'body': body.strip()
                        })
                # Start new commit
                current_commit = [line]
            else:
                # This is part of the commit body
                if line.strip():
                    current_commit.append(line)
        
        # Don't forget the last commit
        if current_commit:
            parts = current_commit[0].split('|', 3)
            if len(parts) == 4:
                commit_hash, date, author, subject = parts
                body = '\n'.join(current_commit[1:]) if len(current_commit) > 1 else ""
                commits.append({
                    'hash': commit_hash[:8],
                    'date': date.split(' ')[0],
                    'author': author,
                    'subject': subject,
                    'body': body.strip()
                })
        
        # Format the commits
        output = []
        for commit in commits:
            output.append(f"- **{commit['hash']}** ({commit['date']}) by {commit['author']}")
            output.append(f"  {commit['subject']}")
            if commit['body']:
                for line in commit['body'].split('\n'):
                    if line.strip():
                        output.append(f"  {line}")
            output.append("")
        
        return '\n'.join(output)
    except subprocess.CalledProcessError:
        return "Unable to retrieve git history (not a git repository or git not available)\n"


def generate_markdown(output_file: str = "codebase_for_llm.md"):
    """Generate the markdown file with codebase content."""
    root_dir = Path.cwd()
    src_dir = root_dir / "src" / "bilancio"
    tests_dir = root_dir / "tests"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("# Bilancio Codebase Documentation\n\n")
        f.write("This document contains the complete codebase structure and content for LLM ingestion.\n\n")
        f.write("---\n\n")
        
        # Project structure
        f.write("## Project Structure\n\n")
        f.write("```\n")
        tree_output = get_tree_output(
            str(root_dir),
            exclude_patterns=[
                '__pycache__*', '*.pyc', '.git', '.pytest_cache', 
                '*.egg-info', '.coverage*', '.venv', 'venv', 'env',
                'htmlcov', '*.ipynb_checkpoints', '.conductor', '.uv',
                '.DS_Store', '.mypy_cache', '.ruff_cache', '.tox', '.nox',
                '.hypothesis', '.env', '.idea', '.vscode', '.claude',
                '*.lock', 'node_modules', '*.log', 'dist', 'build'
            ]
        )
        f.write(tree_output)
        f.write("\n```\n\n")
        f.write("---\n\n")
        
        # Git history section
        f.write("## Git Commit History\n\n")
        f.write("Complete git history from oldest to newest:\n\n")
        git_history = get_git_history()
        f.write(git_history)
        f.write("\n---\n\n")
        
        # Source code section
        f.write("## Source Code (src/bilancio)\n\n")
        f.write("Below are all the Python files in the src/bilancio directory:\n\n")
        
        if src_dir.exists():
            src_files = get_python_files(src_dir)
            
            for file_path in src_files:
                relative_path = file_path.relative_to(root_dir)
                f.write(f"### 📄 {relative_path}\n\n")
                f.write(f"```python\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as src_file:
                        content = src_file.read()
                        f.write(content)
                except Exception as e:
                    f.write(f"# Error reading file: {e}\n")
                
                f.write("\n```\n\n")
                f.write("---\n\n")
        else:
            f.write("*src/bilancio directory not found*\n\n")
        
        # Tests section
        f.write("## Tests\n\n")
        f.write("Below are all the test files:\n\n")
        
        if tests_dir.exists():
            test_files = get_python_files(tests_dir)
            
            for file_path in test_files:
                relative_path = file_path.relative_to(root_dir)
                f.write(f"### 🧪 {relative_path}\n\n")
                f.write(f"```python\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as test_file:
                        content = test_file.read()
                        f.write(content)
                except Exception as e:
                    f.write(f"# Error reading file: {e}\n")
                
                f.write("\n```\n\n")
                f.write("---\n\n")
        else:
            f.write("*tests directory not found*\n\n")
        
        # Footer
        f.write("## End of Codebase\n\n")
        f.write(f"Generated from: {root_dir}\n")
        
        # Get file stats
        total_src_files = len(src_files) if src_dir.exists() else 0
        total_test_files = len(test_files) if tests_dir.exists() else 0
        
        f.write(f"Total source files: {total_src_files}\n")
        f.write(f"Total test files: {total_test_files}\n")
    
    print(f"✅ Markdown file generated: {output_file}")
    print(f"📊 Stats:")
    print(f"   - Source files: {total_src_files}")
    print(f"   - Test files: {total_test_files}")
    
    # Get file size
    file_size = os.path.getsize(output_file)
    print(f"   - Output file size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")


if __name__ == "__main__":
    generate_markdown()