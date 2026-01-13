#!/usr/bin/env python3
"""Modal CLI wrapper that applies proxy patch for TLS-inspecting proxies.

This script applies the bilancio proxy patch before running Modal CLI commands,
allowing Modal to work in environments with HTTP CONNECT proxies that perform
TLS inspection (MITM).

Usage:
    python scripts/modal_wrapper.py app list
    python scripts/modal_wrapper.py volume ls bilancio-results
    python scripts/modal_wrapper.py deploy src/bilancio/cloud/modal_app.py

Or via uv:
    uv run python scripts/modal_wrapper.py app list
"""
import sys

# Apply proxy patch BEFORE importing modal
# This patches grpclib to work through HTTP CONNECT proxy with custom CA
import bilancio.cloud.proxy_patch

# Import and run Modal CLI
from modal.cli.entry_point import entrypoint_cli

if __name__ == "__main__":
    # sys.argv[0] is this script, pass the rest as modal arguments
    # Prepend 'modal' as argv[0] for the CLI parser
    sys.argv = ['modal'] + sys.argv[1:]
    entrypoint_cli()
