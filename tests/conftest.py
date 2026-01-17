"""Pytest configuration and shared fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastmcp import FastMCP

# Import the actual MCP server instance
from scalene_mcp import mcp

# ============================================================================
# Directory Fixtures
# ============================================================================


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def profiles_dir(fixtures_dir: Path) -> Path:
    """Path to sample profile outputs."""
    return fixtures_dir / "profiles"


@pytest.fixture
def scripts_dir(fixtures_dir: Path) -> Path:
    """Path to sample scripts."""
    return fixtures_dir / "scripts"


# ============================================================================
# MCP Server Fixture
# ============================================================================


@pytest.fixture
def server() -> FastMCP:
    """FastMCP server instance for testing."""
    return mcp


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_profile_simple(profiles_dir: Path) -> dict:
    """Simple profile data for basic tests."""
    # Will be populated in Phase 1.2
    return {
        "elapsed_time_seconds": 1.234,
        "files": {},
        "max_footprint_mb": 50.0,
    }


@pytest.fixture
def fibonacci_script(scripts_dir: Path) -> Path:
    """Path to fibonacci test script."""
    return scripts_dir / "fibonacci.py"


@pytest.fixture
def memory_heavy_script(scripts_dir: Path) -> Path:
    """Path to memory-intensive test script."""
    return scripts_dir / "memory_heavy.py"


@pytest.fixture
def leaky_script(scripts_dir: Path) -> Path:
    """Path to script with memory leaks."""
    return scripts_dir / "leaky.py"
