# Scalene-MCP

A FastMCP v2 server providing LLMs with structured access to [Scalene](https://github.com/plasma-umass/scalene)'s comprehensive CPU, GPU, and memory profiling capabilities.

## Installation

### Prerequisites

- Python 3.10+
- uv (recommended) or pip

### From Source

```bash
git clone https://github.com/plasma-umass/scalene-mcp.git
cd scalene-mcp
uv venv
uv sync
```

### As a Package

```bash
pip install scalene-mcp
```

## Quick Start: Running the Server

### Development Mode

```bash
# Using uv
uv run scalene_mcp.server

# Using pip
python -m scalene_mcp.server
```

### Production Mode

```bash
python -m scalene_mcp.server
```

### Available Serving Methods (FastMCP)

Scalene-MCP can be served in multiple ways using FastMCP's built-in serving capabilities:

#### 1. **Standard Server (Default)**
```bash
# Starts an MCP-compatible server on stdio
python -m scalene_mcp.server
```

#### 2. **With Claude Desktop**
Configure in your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scalene": {
      "command": "python",
      "args": ["-m", "scalene_mcp.server"]
    }
  }
}
```

Then restart Claude Desktop.

#### 3. **With HTTP/SSE Endpoint**
```bash
# If using fastmcp with HTTP support
uv run --help  # Check FastMCP documentation for HTTP serving
```

#### 4. **With Environment Variables**
```bash
# Configure via environment
export SCALENE_PYTHON_EXECUTABLE=python3.11
export SCALENE_TIMEOUT=30
python -m scalene_mcp.server
```

#### 5. **Programmatically**
```python
from fastmcp import Server

# Create and run server programmatically
server = create_scalene_server()
# Configure and start...
```

## Programmatic Usage

Use Scalene-MCP directly in your Python code:

```python
from scalene_mcp.profiler import ScaleneProfiler
import asyncio

async def main():
    profiler = ScaleneProfiler()
    
    # Profile a script
    result = await profiler.profile_script(
        "fibonacci.py",
        cpu=True,
        memory=True,
        gpu=False
    )
    
    print(f"Profiled in {result.summary.elapsed_time_sec:.2f}s")
    print(f"Peak memory: {result.summary.max_footprint_mb:.1f}MB")
    
asyncio.run(main())
```

## Overview

Scalene-MCP transforms Scalene's powerful profiling output into an LLM-friendly format through a clean, minimal set of well-designed tools. Get detailed performance insights without images or excessive context overhead.

### What Scalene-MCP Does

- ✅ **Profile Python scripts** with full Scalene feature set
- ✅ **Analyze profiles** for hotspots, bottlenecks, memory leaks
- ✅ **Compare profiles** to detect regressions
- ✅ **Pass arguments** to profiled scripts
- ✅ **Structured output** in JSON format for LLMs
- ✅ **Async execution** for non-blocking profiling

### What Scalene-MCP Doesn't Do

- ❌ **In-process profiling** (`Scalene.start()`/`stop()`) - uses subprocess instead for isolation
- ❌ **Process attachment** (`--pid` based profiling) - profiles scripts, not running processes
- ❌ **Single-function profiling** - designed for complete script analysis

**Note**: The subprocess-based approach was chosen for reliability and simplicity. LLM workflows typically profile complete scripts, which is a perfect fit. See [SCALENE_MODES_ANALYSIS.md](./SCALENE_MODES_ANALYSIS.md) for detailed scope analysis.

### Key Features

- **Complete CPU profiling**: Line-by-line Python/C time, system time, CPU utilization
- **Memory profiling**: Peak/average memory per line, leak detection with velocity metrics
- **GPU profiling**: NVIDIA and Apple GPU support with per-line attribution
- **Advanced analysis**: Stack traces, bottleneck identification, performance recommendations
- **Profile comparison**: Track performance changes across runs
- **LLM-optimized**: Structured JSON output, summaries before details, context-aware formatting

## Available Tools

### Core Profiling

- **profile_script**: Profile a Python script with customizable options
- **profile_code**: Profile a code snippet directly

### Analysis

- **analyze_profile**: Get comprehensive analysis of a profile
- **get_cpu_hotspots**: Find CPU-intensive lines
- **get_memory_hotspots**: Identify memory-heavy code
- **get_gpu_hotspots**: Locate GPU-intensive operations
- **get_bottlenecks**: Identify performance bottlenecks by severity
- **get_memory_leaks**: Detect potential memory leaks
- **get_function_summary**: Aggregate metrics by function

### Comparison & Storage

- **compare_profiles**: Compare two profiles to identify changes
- **list_profiles**: View stored profiles
- **get_profile**: Retrieve a specific profile
- **get_file_details**: Get per-file metrics and context

## Configuration

### Profiling Options

All profiling tools support these options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cpu` | bool | true | Profile CPU time |
| `memory` | bool | true | Profile memory |
| `gpu` | bool | false | Profile GPU usage |
| `stacks` | bool | false | Collect stack traces |
| `cpu_sampling_rate` | float | 0.01 | CPU sampling interval (seconds) |
| `cpu_percent_threshold` | float | 1.0 | Minimum CPU% to report |
| `malloc_threshold` | int | 100 | Minimum allocation size (bytes) |
| `profile_only` | str | "" | Profile only paths containing this |
| `profile_exclude` | str | "" | Exclude paths containing this |
| `reduced_profile` | bool | false | Only report high-activity lines |
| `use_virtual_time` | bool | false | Use virtual time instead of wall time |
| `memory_leak_detector` | bool | true | Enable leak detection |

### Environment Variables

- `SCALENE_CPU_PERCENT_THRESHOLD`: Override default CPU threshold
- `SCALENE_MALLOC_THRESHOLD`: Override default malloc threshold

## Architecture

### Components

- **ScaleneProfiler**: Async wrapper around Scalene CLI
- **ProfileParser**: Converts Scalene JSON to structured models
- **ProfileAnalyzer**: Extracts insights and hotspots
- **ProfileComparator**: Compares profiles for regressions
- **FastMCP Server**: Exposes tools via MCP protocol

### Data Flow

```
Python Script
    ↓
ScaleneProfiler (subprocess)
    ↓
Scalene CLI (--json)
    ↓
Temp JSON File
    ↓
ProfileParser
    ↓
Pydantic Models (ProfileResult)
    ↓
Analyzer / Comparator
    ↓
MCP Tools
    ↓
LLM Client
```

## Troubleshooting

### GPU Permission Error

If you see `PermissionError` when profiling with GPU:

```python
# Disable GPU profiling in test environments
result = await profiler.profile_script("script.py", gpu=False)
```

### Profile Not Found

Profiles are stored in memory during the server session. For persistence, implement the storage interface.

### Timeout Issues

Adjust the timeout parameter:

```python
result = await profiler.profile_script(
    "slow_script.py",
    timeout=30.0  # 30 seconds
)
```

## Development

### Running Tests

```bash
# All tests with coverage
uv run pytest -v --cov=src/scalene_mcp

# Specific test file
uv run pytest tests/test_profiler.py -v

# With coverage report
uv run pytest --cov=src/scalene_mcp --cov-report=html
```

### Code Quality

```bash
# Type checking
uv run mypy src/

# Linting
uv run ruff check src/

# Formatting
uv run ruff format src/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass and coverage ≥ 85%
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Citation

If you use Scalene-MCP in research, please cite both this project and Scalene:

```bibtex
@software{scalene_mcp,
  title={Scalene-MCP: LLM-Friendly Profiling Server},
  year={2026}
}

@inproceedings{berger2020scalene,
  title={Scalene: Scripting-Language Aware Profiling for Python},
  author={Berger, Emery},
  year={2020}
}
```

## Support

- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and ideas
- **Documentation**: See `docs/` directory

---

Made with ❤️ for the Python performance community.

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
