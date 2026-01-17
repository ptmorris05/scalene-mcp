# Scalene MCP

**Professional MCP server for Scalene profiler — LLM-optimized access to CPU, GPU, and memory profiling**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0+-green.svg)](https://github.com/jlowin/fastmcp)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Overview

Scalene MCP provides a Model Context Protocol (MCP) server that makes Scalene's comprehensive Python profiling capabilities accessible to Large Language Models. Through a minimal, well-designed interface of 3 powerful tools, 7 data resources, and 5 workflow prompts, LLMs can help you profile code, analyze performance bottlenecks, detect memory leaks, and optimize Python applications.

**Key Features:**
- **Comprehensive Profiling:** CPU (Python/C/system), GPU, and memory profiling via Scalene
- **LLM-Friendly Design:** Minimal tool surface with comprehensive parameters
- **Production Ready:** 100% test coverage, strict type checking, professional code quality
- **Flexible Deployment:** Supports script paths and code snippets
- **Rich Analysis:** Automated hotspot detection, leak detection, and optimization recommendations

## Architecture

### Tools (3)
- **`profile`** - Execute profiling with full Scalene option control
- **`analyze`** - Generate insights and recommendations from profile data
- **`compare`** - Compare multiple profiles to identify regressions/improvements

### Resources (7)
- **`profile://{id}`** - Access raw profile data
- **`profile://{id}/summary`** - Get high-level summary
- **`profile://{id}/hotspots`** - Retrieve CPU/memory hotspots
- **`profile://{id}/leaks`** - Access memory leak detections
- **`profile://{id}/functions`** - Function-level metrics
- **`profile://{id}/files/{file}`** - File-specific line-by-line data
- **`profile://list`** - List all available profiles

### Prompts (5)
- **`quick_profile`** - Fast profiling workflow
- **`deep_analysis`** - Comprehensive performance analysis
- **`memory_investigation`** - Focus on memory usage and leaks
- **`optimization_guide`** - Step-by-step optimization recommendations
- **`compare_versions`** - Before/after comparison workflow

## Installation

### Using uv (Recommended)

```bash
git clone <repository>
cd scalene-mcp
uv sync
```

### Manual Installation

```bash
pip install -e .
```

## Development

### Prerequisites
- Python 3.10+
- uv (recommended) or pip

### Setup

```bash
# Install dependencies
uv sync

# Run tests
just test

# Run tests with coverage
just test-cov

# Lint and format
just lint
just format

# Type check
just typecheck

# Full build (sync + lint + typecheck + test)
just build
```

### Project Structure

```
scalene-mcp/
├── src/scalene_mcp/     # Main package
│   ├── server.py        # FastMCP server with tools/resources/prompts
│   ├── models.py        # Pydantic data models
│   ├── profiler.py      # Scalene execution wrapper
│   ├── parser.py        # JSON output parser
│   ├── analyzer.py      # Analysis engine
│   ├── comparator.py    # Profile comparison
│   ├── recommender.py   # Optimization recommendations
│   ├── storage.py       # Profile persistence
│   └── utils.py         # Shared utilities
├── tests/               # Test suite (100% coverage goal)
│   ├── fixtures/        # Test data
│   │   ├── profiles/    # Sample profile outputs
│   │   └── scripts/     # Test Python scripts
│   └── conftest.py      # Shared test fixtures
├── examples/            # Usage examples
├── docs/                # Documentation
├── pyproject.toml       # Project configuration
├── justfile             # Task runner commands
└── README.md            # This file
```

## Usage

### Running the Server

```bash
# Development mode with auto-reload
fastmcp dev src/scalene_mcp/server.py

# Production mode
fastmcp run src/scalene_mcp/server.py

# Install to MCP config
fastmcp install src/scalene_mcp/server.py
```

### Example: Profile a Script

```python
# Through MCP client
result = await client.call_tool(
    "profile",
    arguments={
        "script_path": "my_script.py",
        "cpu": True,
        "memory": True,
        "gpu": False,
    }
)
```

### Example: Analyze Results

```python
# Get analysis and recommendations
analysis = await client.call_tool(
    "analyze",
    arguments={"profile_id": result["profile_id"]}
)
```

## Testing

The project maintains 100% test coverage with comprehensive test suites:

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_server.py

# Run with verbose output
uv run pytest -v
```

Test fixtures include:
- Sample profiling scripts (fibonacci, memory-intensive, leaky)
- Realistic Scalene JSON outputs
- Edge cases and error conditions

## Code Quality

This project follows strict code quality standards:

- **Type Safety:** 100% mypy strict mode compliance
- **Linting:** ruff with comprehensive rules
- **Testing:** 100% coverage requirement
- **Style:** Sleek-modern documentation, minimal functional emoji usage
- **Patterns:** FastMCP best practices throughout

## Development Phases

Current Status: **Phase 1.1 - Project Setup** ✓

1. **Phase 1:** Project Setup & Infrastructure ✓
2. **Phase 2:** Core Data Models (In Progress)
3. **Phase 3:** Profiler Integration
4. **Phase 4:** Analysis & Insights
5. **Phase 5:** Comparison Features
6. **Phase 6:** Resources Implementation
7. **Phase 7:** Prompts & Workflows
8. **Phase 8:** Testing & Quality
9. **Phase 9:** Documentation
10. **Phase 10:** Polish & Release

See [development-plan.md](../development-plan.md) for detailed roadmap.

## Contributing

Contributions are welcome! Please ensure:
- All tests pass (`just test`)
- Linting passes (`just lint`)
- Type checking passes (`just typecheck`)
- Code coverage remains at 100%

## License

[License TBD]

## Links

- [Scalene Profiler](https://github.com/plasma-umass/scalene)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
