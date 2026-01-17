# Phase 9: Polish & 100% Coverage

**Status**: Planning
**Previous Phases**: 1-8 Complete
**Current Coverage**: 85.62% (744 statements, 107 missing)
**Current Tests**: 155 passing

## Strategic Objective

Achieve production-ready quality through:
1. **100% test coverage** - Cover all code paths
2. **Quality assurance** - Linting, type checking, documentation
3. **Performance validation** - Overhead profiling, stress testing
4. **Release preparation** - Version, changelog, package validation

## Current Coverage Analysis

### Coverage by Module (155 statements total)

| Module | Coverage | Missing Lines | Status |
|--------|----------|----------------|--------|
| `models.py` | 100% (128) | 0 | ✅ Perfect |
| `server.py` | 98.18% (110) | 2 | 🟡 2 lines missing |
| `comparator.py` | 93.75% (96) | 6 | 🟡 6 lines missing |
| `parser.py` | 96.55% (87) | 3 | 🟡 3 lines missing |
| `logging.py` | 88.89% (18) | 2 | 🟡 2 lines missing |
| `analyzer.py` | 86.93% (153) | 20 | 🟠 20 lines missing |
| `profiler.py` | 83.33% (90) | 15 | 🟠 15 lines missing |
| `__init__.py` | 100% (3) | 0 | ✅ Perfect |
| `config.py` | 100% (0) | 0 | ✅ Perfect (empty) |
| `recommender.py` | 100% (0) | 0 | ✅ Perfect (empty) |
| `utils.py` | 100% (0) | 0 | ✅ Perfect (empty) |
| **storage.py** | **0% (59)** | **59** | 🔴 **Not tested** |

**Coverage Gap**: 107 missing statements
- **High Priority**: `storage.py` (0% - 59 statements)
- **Medium Priority**: `profiler.py` (15 missing), `analyzer.py` (20 missing)
- **Low Priority**: Other modules (<3 lines each)

## Detailed Coverage Gaps & Fixes

### 🔴 CRITICAL: storage.py (0% coverage - 59 statements)

**Current State**: Module exists but has zero test coverage

**Missing Coverage**:
- ProfileStorage initialization and configuration
- Profile storage operations (save, retrieve)
- Dictionary-based in-memory storage
- Edge cases and error handling
- Integration with server

**Fix Strategy**:
1. Create `tests/test_storage.py` with comprehensive test suite
2. Test ProfileStorage initialization
3. Test profile storage/retrieval operations
4. Test storage limits and eviction
5. Test persistence flags
6. Test thread safety (if applicable)
7. Test error conditions

**Estimated Effort**: ~20 test cases, 2-3 hours

---

### 🟠 HIGH: analyzer.py (86.93% coverage - 20 missing)

**Uncovered Lines**: 159, 166-167, 243-244, 264, 285, 295-303, 321, 348, 354, 407-413

**Missing Coverage Analysis**:

| Lines | Function | Issue | Fix |
|-------|----------|-------|-----|
| 159, 166-167 | `get_cpu_hotspots()` | Edge cases | Test with empty/minimal profiles |
| 243-244 | `get_memory_hotspots()` | Sorting logic | Test memory threshold edge cases |
| 264 | `get_bottlenecks()` | No bottlenecks case | Test profile with no hotspots |
| 285 | `get_memory_leaks()` | Leak detection logic | Test various leak scenarios |
| 295-303 | Leak recommendation | Edge case branches | Test borderline leak detection |
| 321 | `get_function_summary()` | Unknown function | Test missing function lookup |
| 348, 354 | Stack aggregation | Optional stacks | Test with/without stack traces |
| 407-413 | Exception handling | Error conditions | Test invalid inputs, timeouts |

**Fix Strategy**:
1. Identify exact uncovered code paths
2. Create targeted test fixtures
3. Add parametrized tests for edge cases
4. Test error conditions and boundaries

**Estimated Effort**: ~15 test cases, 2 hours

---

### 🟠 HIGH: profiler.py (83.33% coverage - 15 missing)

**Uncovered Lines**: 111, 115, 119, 121, 123, 135, 141, 143, 145, 182-183, 197-198, 208-209

**Missing Coverage Analysis**:

| Lines | Context | Issue | Fix |
|-------|---------|-------|-----|
| 111, 115, 119, 121, 123 | Argument validation | Optional flags | Test with various flag combinations |
| 135, 141, 143, 145 | Command building | Conditional args | Test all command paths |
| 182-183 | Process timeout | Timeout path | Test with short timeout |
| 197-198 | Timeout cleanup | Kill process path | Test process killing |
| 208-209 | Exception handling | Rare errors | Test process failures |

**Fix Strategy**:
1. Mock subprocess execution paths
2. Test error scenarios (timeouts, process failures)
3. Test various argument combinations
4. Test timeout recovery

**Estimated Effort**: ~12 test cases, 2 hours

---

### 🟡 MEDIUM: analyzer.py specifics

**Line 159**: `get_cpu_hotspots()` with empty profile
**Line 166-167**: CPU time filtering logic
- Test with profile where no lines meet threshold
- Test boundary conditions for percentage

**Line 243-244**: `get_memory_hotspots()` sorting
- Test profiles sorted by different metrics
- Test with all lines below threshold

**Line 264**: `get_bottlenecks()` empty result
- Test profile with no identifiable bottlenecks
- Test when bottleneck score is zero across board

**Lines 285, 295-303**: Memory leak detection
- Test borderline leak candidates
- Test various velocity values
- Test with zero memory growth

**Line 321**: Function lookup failure
- Test requesting summary for non-existent function
- Test with partial function names

**Lines 348, 354**: Stack trace handling
- Test profile without stack traces
- Test with empty stack information

**Lines 407-413**: Recommendation edge cases
- Test unknown analysis types
- Test with incomplete profile data
- Test exception propagation

---

### 🟡 LOW: comparator.py (93.75% coverage - 6 missing)

**Uncovered Lines**: 144, 160, 254, 327-339

**Missing Coverage**:
- Edge cases in comparison logic
- Error handling paths
- Boundary conditions

**Fix Strategy**:
1. Test comparison with empty profiles
2. Test with identical profiles
3. Test edge case deltas

**Estimated Effort**: ~5 test cases, 1 hour

---

### 🟡 LOW: parser.py (96.55% coverage - 3 missing)

**Uncovered Lines**: 56-57, 61

**Missing Coverage**:
- Error handling for malformed JSON
- Edge cases in schema parsing

**Fix Strategy**:
1. Test with invalid JSON
2. Test with missing required fields
3. Test with extra unexpected fields

**Estimated Effort**: ~3 test cases, 30 minutes

---

### 🟡 LOW: server.py (98.18% coverage - 2 missing)

**Uncovered Lines**: 666, 670

**Missing Coverage**:
- Likely exception handling paths
- Unlikely code branches

**Fix Strategy**:
1. Identify exact paths
2. Create minimal test case
3. May not be critical for functionality

**Estimated Effort**: ~2 test cases, 30 minutes

---

### 🟡 LOW: logging.py (88.89% coverage - 2 missing)

**Uncovered Lines**: 22, 38

**Missing Coverage**:
- Different logging level initialization
- Logger configuration edge cases

**Fix Strategy**:
1. Test with different log levels
2. Test logger initialization variations

**Estimated Effort**: ~2 test cases, 30 minutes

---

## Phase 9 Implementation Plan

### Task 1: Storage Testing (Critical - 2-3 hours)

**File**: `tests/test_storage.py`

```python
# Test categories:
class TestProfileStorage:
    # Initialization tests
    test_storage_initialization()
    test_storage_with_max_profiles()
    
    # Storage operations
    test_store_profile()
    test_retrieve_profile()
    test_list_profiles()
    test_get_nonexistent_profile()
    
    # Edge cases
    test_store_multiple_profiles()
    test_storage_limit_eviction()
    test_clear_storage()
    
    # Integration
    test_storage_with_server()
```

**Success Criteria**: 100% coverage of `storage.py`

---

### Task 2: Profiler Testing (Medium - 2 hours)

**Locations**: `tests/test_profiler.py` (expand existing)

**Test scenarios**:
- Timeout handling (mock `asyncio.TimeoutError`)
- Process failures (mock `RuntimeError`)
- Missing output file handling
- Various argument combinations
- Profile argument edge cases

**Tools needed**:
- `unittest.mock.patch` for subprocess
- Fixtures for various argument sets
- Temporary files for output

**Success Criteria**: 100% coverage of `profiler.py`

---

### Task 3: Analyzer Testing (Medium - 2 hours)

**Locations**: `tests/test_analyzer.py` (expand existing)

**Test scenarios**:
- Empty profiles
- Profiles with no hotspots
- Profiles below thresholds
- Memory leak boundary cases
- Missing stack traces
- Unknown function lookups
- Various bottleneck profiles

**Tools needed**:
- Parametrized fixtures
- Boundary value analysis
- Error condition fixtures

**Success Criteria**: 100% coverage of `analyzer.py`

---

### Task 4: Comparator Testing (Low - 1 hour)

**Locations**: `tests/test_comparator.py` (expand existing)

**Test scenarios**:
- Empty profile comparison
- Identical profiles
- Profiles with zero differences
- Edge case deltas

**Success Criteria**: 100% coverage of `comparator.py`

---

### Task 5: Parser Testing (Low - 30 minutes)

**Locations**: `tests/test_parser.py` (expand existing)

**Test scenarios**:
- Malformed JSON input
- Missing required fields
- Extra unexpected fields
- Incomplete profile data

**Success Criteria**: 100% coverage of `parser.py`

---

### Task 6: Server & Logging Testing (Low - 1 hour)

**Locations**: `tests/test_server.py`, `tests/test_logging.py`

**Test scenarios**:
- Remaining server exception paths
- Different logging levels
- Logger initialization variations

**Success Criteria**: 100% coverage of both modules

---

## Testing Best Practices

### 1. Test Organization

```
tests/
├── test_models.py (existing - 100%)
├── test_parser.py (existing - enhance)
├── test_profiler.py (existing - enhance)
├── test_analyzer.py (existing - enhance)
├── test_comparator.py (existing - enhance)
├── test_storage.py (NEW - critical)
├── test_logging.py (existing - enhance)
├── test_server.py (existing - enhance)
├── test_examples.py (existing - enhance)
├── conftest.py (fixtures)
└── fixtures/ (test data)
```

### 2. Coverage Tracking

```bash
# Run with coverage report
uv run pytest --cov=src/scalene_mcp --cov-report=html

# View missing lines
uv run pytest --cov=src/scalene_mcp --cov-report=term-missing

# Fail if below threshold
uv run pytest --cov=src/scalene_mcp --cov-fail-under=100
```

### 3. Parametrized Tests

Use `pytest.mark.parametrize` for edge cases:

```python
@pytest.mark.parametrize("profile,expected", [
    (empty_profile, []),
    (minimal_profile, [hotspot]),
    (full_profile, [hotspot1, hotspot2]),
])
def test_get_hotspots(profile, expected):
    # Test multiple scenarios
```

### 4. Fixtures for Profiles

Create reusable test profiles:

```python
@pytest.fixture
def empty_profile():
    """Profile with no data"""
    
@pytest.fixture
def minimal_profile():
    """Smallest valid profile"""
    
@pytest.fixture
def full_profile():
    """Complex profile with all features"""
```

---

## Quality Assurance Checklist

### 9.1 Testing (6-8 hours)

- [ ] storage.py: 59 statements → 59 covered
- [ ] profiler.py: 90 statements → 90 covered
- [ ] analyzer.py: 153 statements → 153 covered
- [ ] comparator.py: 96 statements → 96 covered
- [ ] parser.py: 87 statements → 87 covered
- [ ] server.py: 110 statements → 110 covered
- [ ] logging.py: 18 statements → 18 covered
- [ ] Run full test suite: `uv run pytest -v`
- [ ] Achieve 100% coverage: `uv run pytest --cov --cov-fail-under=100`
- [ ] Fix all warnings in test output

**Success Metric**: `TOTAL 744 100.0%`

### 9.2 Type Checking (1-2 hours)

```bash
# Full type checking
uv run mypy src/

# Per-module checking
uv run mypy src/scalene_mcp/profiler.py
uv run mypy src/scalene_mcp/analyzer.py
# ... etc
```

**Success Criteria**:
- No type errors
- All functions have type hints
- All imports properly typed

### 9.3 Linting (1 hour)

```bash
# Check code style
uv run ruff check src/

# Fix automatically
uv run ruff check src/ --fix

# Format code
uv run ruff format src/
```

**Success Criteria**:
- No style violations
- Consistent formatting
- No unused imports

### 9.4 Documentation Review (1 hour)

- [ ] README.md
  - Renders correctly on GitHub
  - Installation instructions clear
  - Quick start works end-to-end
  - All examples accurate
  - No broken links

- [ ] API Documentation
  - All tools documented
  - Parameters clearly described
  - Return values specified
  - Error conditions listed
  - Examples for each tool

- [ ] Architecture Documentation
  - Dataflow diagram accurate
  - Component descriptions clear
  - Design decisions explained

- [ ] Docstrings
  - All public functions/classes documented
  - Parameter types and descriptions
  - Return value descriptions
  - Raises clauses for exceptions
  - Example usage where helpful

### 9.5 Performance Testing (1-2 hours)

```bash
# Profile the profiler
python -m scalene examples/profile_profiler.py

# Test with large codebases
python -m scalene large_project.py

# Test server memory usage
python -m scalene -m scalene_mcp.server
```

**Success Criteria**:
- Profiler overhead < 10% of target script time
- Server memory < 50MB baseline
- No memory leaks in long-running server

### 9.6 Python Version Testing (1 hour)

Test on supported Python versions:
- [ ] Python 3.10 (primary)
- [ ] Python 3.11
- [ ] Python 3.12
- [ ] Python 3.13 (if available)

```bash
# Test with different Python versions
python3.10 -m venv venv3.10
python3.11 -m venv venv3.11
# ... activate and test each
```

### 9.7 Installation Testing (30 minutes)

```bash
# Test pip installation
pip install -e .
python -m scalene_mcp.server

# Test package installation
pip install .
python -m scalene_mcp.server

# Test in clean environment
cd /tmp
python -m venv testenv
./testenv/bin/pip install /path/to/scalene-mcp
./testenv/bin/python -m scalene_mcp.server
```

### 9.8 Example Validation (30 minutes)

- [ ] All examples run without errors
- [ ] Examples complete in expected time
- [ ] Examples produce expected output
- [ ] Examples work with latest Scalene version

---

## Release Preparation Tasks

### Version Management

**Current**: Working toward v0.1.0

**File**: `pyproject.toml`
- Update version from dev to 0.1.0
- Review dependencies
- Check Python version constraints

### Changelog

**File**: `CHANGELOG.md`

Structure:
```markdown
## [0.1.0] - 2026-01-XX

### Added
- Complete Scalene-MCP v0.1.0 implementation
- 12 MCP tools for profiling and analysis
- Support for CPU, GPU, memory profiling
- Profile comparison and storage
- FastMCP v2 server integration
- 100+ examples and documentation

### Fixed
- [list any bug fixes]

### Changed
- [list any breaking changes or major changes]

### Known Issues
- [list any known limitations]
```

### Package Validation

```bash
# Build package
uv build

# Check package contents
tar -tzf dist/scalene-mcp-0.1.0.tar.gz | head -20

# Test installation
pip install dist/scalene_mcp-0.1.0-py3-none-any.whl

# Verify functionality
python -m scalene_mcp.server --help
```

### Git Release

```bash
# Create release tag
git tag -a v0.1.0 -m "Release v0.1.0: Initial Scalene-MCP release"

# Push to remote
git push origin v0.1.0
```

---

## Success Metrics for Phase 9

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Test Coverage | 100% | 85.62% | 🔴 Gap: 14.38% |
| Tests Passing | 100% | 155/155 (100%) | ✅ |
| Type Checking | 0 errors | ? | 🟡 TBD |
| Lint Score | 0 issues | ? | 🟡 TBD |
| Docstring Coverage | 100% | ? | 🟡 TBD |
| Python Versions | 3.10-3.13 | 3.10 tested | 🟡 Partial |
| Installation Success | 100% | ? | 🟡 TBD |
| Documentation Quality | Professional | Good | ✅ High |

---

## Estimated Timeline

| Task | Hours | Days |
|------|-------|------|
| Storage Testing (critical) | 2-3 | 0.25-0.38 |
| Profiler Testing (high) | 2 | 0.25 |
| Analyzer Testing (high) | 2 | 0.25 |
| Comparator Testing (med) | 1 | 0.13 |
| Parser Testing (low) | 0.5 | 0.06 |
| Server/Logging Testing (low) | 1 | 0.13 |
| **Testing Subtotal** | **8.5-9.5** | **1.1-1.2** |
| Type Checking & Fixes | 1-2 | 0.13-0.25 |
| Linting & Formatting | 1 | 0.13 |
| Documentation Review | 1 | 0.13 |
| Performance Testing | 1-2 | 0.13-0.25 |
| Python Version Testing | 1 | 0.13 |
| Installation Testing | 0.5 | 0.06 |
| Release Preparation | 1 | 0.13 |
| **Total Phase 9** | **15-18** | **2.0-2.3** |

**Expected Duration**: 2-2.5 days

---

## Risk Analysis

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Coverage hard to reach | Low | High | Comprehensive test fixtures |
| Performance regression | Low | Medium | Baseline profiling before/after |
| Python version incompatibility | Medium | Medium | Test all supported versions |
| Scalene version changes | Low | Medium | Pin Scalene version in tests |

### Timeline Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Test writing slower than expected | Medium | High | Pair programming, templates |
| Debugging coverage gaps | Medium | Medium | Incremental testing approach |
| Documentation gaps discovered | Low | Low | Review before release |

---

## Phase 9 Success Checklist

### Coverage: All Modules at 100%
- [ ] `storage.py`: 0% → 100% (59 statements)
- [ ] `profiler.py`: 83.33% → 100% (15 statements)
- [ ] `analyzer.py`: 86.93% → 100% (20 statements)
- [ ] `comparator.py`: 93.75% → 100% (6 statements)
- [ ] `parser.py`: 96.55% → 100% (3 statements)
- [ ] `server.py`: 98.18% → 100% (2 statements)
- [ ] `logging.py`: 88.89% → 100% (2 statements)
- [ ] All other modules: Already at 100%

### Quality Assurance Complete
- [ ] `uv run pytest -v` - All tests pass
- [ ] `uv run pytest --cov --cov-fail-under=100` - 100% coverage
- [ ] `uv run mypy src/` - No type errors
- [ ] `uv run ruff check src/` - No lint issues
- [ ] `uv run ruff format src/` - Consistent formatting

### Documentation Complete
- [ ] README renders correctly on GitHub
- [ ] All API documentation up-to-date
- [ ] All docstrings present and accurate
- [ ] Examples all functional and tested

### Release Ready
- [ ] Version updated to 0.1.0
- [ ] CHANGELOG.md written
- [ ] Package builds successfully
- [ ] Installation tested on clean system
- [ ] Git tag created: v0.1.0

---

## What Comes After Phase 9?

**Phase 10: Advanced Features** (v0.2.0+)

Once Phase 9 is complete and v0.1.0 is released, Phase 10 would include:

- [ ] Stack trace collection and analysis (`--stacks`)
- [ ] Historical profile tracking
- [ ] Smart caching of profiles
- [ ] Visualization generation (charts from data)
- [ ] Automatic optimization suggestions
- [ ] CI/CD integration templates
- [ ] VS Code extension
- [ ] GitHub Actions integration
- [ ] Remote profiling capabilities

**Estimated Release**: Q2 2026

---

## Resources & References

- [Pytest Coverage](https://pytest-cov.readthedocs.io/)
- [MyPy Type Checking](https://mypy.readthedocs.io/)
- [Ruff Linting](https://docs.astral.sh/ruff/)
- [Scalene Documentation](https://github.com/plasma-umass/scalene)
- [FastMCP Server](https://github.com/jlowin/fastmcp)
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
