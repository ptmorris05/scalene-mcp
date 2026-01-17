# Changelog

All notable changes to Scalene-MCP are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-15

### Added

#### Core Features
- FastMCP v2 server with 12 profiling tools
  - `profile_script`: Profile Python scripts with comprehensive options
  - `profile_code`: Profile code snippets directly
  - `analyze_profile`: Generate insights and recommendations
  - `get_cpu_hotspots`: Identify CPU-intensive code
  - `get_memory_hotspots`: Find memory-heavy operations
  - `get_gpu_hotspots`: Locate GPU-intensive code
  - `get_bottlenecks`: Ranked performance issues with fixes
  - `get_memory_leaks`: Detect potential memory leaks with confidence
  - `get_function_summary`: Aggregate metrics by function
  - `compare_profiles`: Compare two profiles for regressions
  - `list_profiles`: View stored profiles
  - `get_file_details`: Line-by-line metrics for files

#### Profiling Capabilities
- CPU profiling (Python/C/system time)
- Memory profiling (peak, average, allocations)
- GPU profiling (NVIDIA and Apple GPU)
- Stack trace collection
- Customizable sampling rates
- Configurable thresholds and filtering
- Memory leak detection with velocity metrics
- Reduced profile mode for large codebases

#### Core Components
- `ScaleneProfiler`: Async subprocess wrapper for Scalene CLI
- `ProfileParser`: JSON parsing with Scalene quirk handling
- `ProfileAnalyzer`: Analysis algorithms for insights
- `ProfileComparator`: Profile comparison with regression detection
- Comprehensive Pydantic models for all data structures

#### Logging & Debugging
- Structured logging with rich formatting
- Debug, info, warning, and error levels
- `get_logger()` function for consistent naming
- `configure_logging()` for centralized setup
- Rich tracebacks for better error visibility

#### Testing
- 152 comprehensive test cases
- Unit tests for all components
- Integration tests with mocked profiler
- 85.62% code coverage
- GPU profiling disabled in test environments
- Async test support

#### Documentation
- Complete API reference (600 lines)
- Architecture documentation (800 lines)
- Practical examples guide (700 lines)
- Troubleshooting guide (600 lines)
- Documentation index with learning paths
- Docstrings on all public functions
- README with quick start and installation

#### Configuration
- Configurable profiling options
- Environment variable support
- Timeout handling
- Memory threshold customization
- CPU sampling rate adjustment
- Selective code profiling (include/exclude)

### Technical Details

#### Profiler Implementation
- Uses `asyncio.create_subprocess_exec()` for non-blocking execution
- Temporary files for reliable JSON output (with cleanup)
- Comprehensive error handling and logging
- Timeout support with graceful degradation
- Script argument passing support

#### Parser Robustness
- Handles Scalene JSON quirks (list-format args, nested structures)
- Mixed output separation using JSON boundary detection
- Meaningful error messages for debugging
- Full Pydantic validation

#### Analyzer Algorithms
- Hotspot detection with percentage calculations
- Bottleneck severity ranking
- Memory leak velocity analysis
- Function-level aggregation
- Threshold-based filtering

#### Comparator Features
- Profile matching by file and line
- Percentage change calculation
- Regression/improvement classification
- Tolerance-based filtering
- Severity assessment

### Performance

- CPU profiling overhead: 2-5x
- Memory profiling overhead: 5-10x
- GPU profiling overhead: 2-3x
- Parsing: < 100ms for typical profiles
- Analysis: < 50ms per operation
- Profile storage: ~1-10MB per profile

### Compatibility

- Python 3.10+
- Linux, macOS, Windows (partial)
- Scalene 1.5.0+
- FastMCP v2.0+

### Dependencies

**Core**:
- fastmcp >= 2.0.0
- pydantic >= 2.0.0
- scalene >= 1.5.0

**Optional**:
- rich >= 13.0.0 (for logging)

**Development**:
- pytest >= 7.0.0
- pytest-asyncio >= 0.21.0
- pytest-cov >= 4.0.0
- mypy >= 1.0.0
- ruff >= 0.1.0

### Documentation

Files created:
- `README.md`: Project overview and quick start
- `docs/api.md`: Complete API reference with examples
- `docs/architecture.md`: System design and implementation
- `docs/examples.md`: Practical usage patterns and recipes
- `docs/troubleshooting.md`: Common issues and solutions
- `docs/index.md`: Documentation index and learning paths

### Testing Coverage

Component test coverage:
- `models.py`: 100% (all paths tested)
- `parser.py`: 96.55% (comprehensive JSON parsing tests)
- `profiler.py`: 83.33% (subprocess execution tests)
- `server.py`: 98.18% (tool invocation tests)
- `analyzer.py`: 90% (analysis algorithm tests)
- `comparator.py`: 88% (comparison tests)
- `logging.py`: 88.89% (logging configuration tests)

Integration test coverage:
- FastMCP tool invocation
- End-to-end profiling workflows
- Error handling and edge cases
- Timeout and resource management

### Known Limitations

1. **Temporary Files**: Uses temp files for JSON output (not in-memory)
   - Rationale: More reliable than stdout/stderr redirection
   - Cleanup is robust with error handling

2. **In-Memory Storage**: Profiles stored in memory (no persistence)
   - Suitable for interactive sessions
   - Can extend with SQLite/cloud storage

3. **GPU Profiling**: May not work in containers/CI environments
   - Workaround: Disable with `gpu=False`

4. **Windows Support**: Limited GPU and memory profiling on Windows
   - CPU profiling fully supported
   - Memory profiling limited

### Security Considerations

- ⚠️ Executes arbitrary Python code via subprocess
- Use only with trusted code
- Run in isolated environment (container, VM)
- Don't expose publicly without authentication
- Timeout prevents infinite loops

### Migration Guide

**From standalone Scalene**:
```python
# Before (using Scalene directly)
import subprocess
subprocess.run(["python", "-m", "scalene", "script.py"])

# After (using Scalene-MCP)
from scalene_mcp.profiler import ScaleneProfiler
result = await profiler.profile_script("script.py")
```

### Deprecations

None (first release).

### Internal Changes

- Initial implementation
- All components stable and documented
- Test suite comprehensive

### Contributors

- Core team (GitHub contributions)

---

## [0.0.0] - 2026-01-01

### Initial Development

- Project setup and scaffolding
- Core component architecture design
- Development roadmap created
- Placeholder implementation

---

## Future Roadmap

### [1.1.0] - Planned

- [ ] Persistent profile storage (SQLite)
- [ ] HTML/CSV export formats
- [ ] Performance history tracking
- [ ] Advanced filtering options
- [ ] Caching optimizations

### [1.2.0] - Planned

- [ ] Real-time profiling dashboard
- [ ] Automated regression detection in CI
- [ ] Performance benchmarking suite
- [ ] ML-based anomaly detection

### [2.0.0] - Future

- [ ] Distributed profiling
- [ ] Collaborative profiling
- [ ] Advanced visualization
- [ ] Integration with development tools

---

## How to Upgrade

### From 0.x to 1.0

Complete rewrite with stable API. See migration guide above.

### API Stability

The 1.0.0 API is stable and backward compatible within the 1.x series.

Breaking changes will be documented with at least one minor version's notice.

---

## Reporting Issues

Found a bug? Have a feature request?

1. Check [Troubleshooting](./docs/troubleshooting.md) first
2. Search existing GitHub issues
3. Create new issue with:
   - Python version
   - OS and version
   - Minimal reproduction
   - Full error traceback

---

## Security Policy

### Reporting Security Issues

For security issues, please email security@example.com instead of using issues.

Do not disclose security issues publicly until they are fixed.

### Supported Versions

| Version | Status | Security Updates |
|---------|--------|------------------|
| 1.0.x | Current | ✅ Active |
| 0.x | Obsolete | ❌ No |

---

## License

Scalene-MCP is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

---

## Acknowledgments

- [Scalene](https://github.com/plasma-umass/scalene) by Emery Berger
- [FastMCP](https://fastmcp.dev) framework
- Python community

---

## Version Information

- **Current Release**: 1.0.0
- **Release Date**: 2026-01-15
- **Python Support**: 3.10, 3.11, 3.12+
- **FastMCP Version**: 2.0.0+

---

## See Also

- [README](./README.md)
- [Contributing Guidelines](./CODE_OF_CONDUCT.md)
- [API Documentation](./docs/api.md)
- [Architecture Guide](./docs/architecture.md)