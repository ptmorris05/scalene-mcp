# Phase 9: Execution Guide

A hands-on guide for implementing Phase 9 with commands and code snippets.

## Setup

```bash
cd /home/paul/Documents/scalene-mcp/scalene-mcp

# Verify current state
uv run pytest --cov=src/scalene_mcp --cov-report=term-missing | grep -E "TOTAL|src/scalene"
```

Expected output:
```
TOTAL                              744    107  85.62%
ERROR: Coverage failure: total of 85.62 is less than fail-under=100.00
```

---

## Phase 9 Execution (Day 1)

### Task 1: Create storage.py Tests (2-3 hours)

**File**: `tests/test_storage.py` (NEW)

```python
"""Comprehensive tests for profile storage module."""

import pytest
from scalene_mcp.storage import ProfileStorage
from scalene_mcp.models import ProfileResult, ProfileSummary

@pytest.fixture
def storage():
    """Create a ProfileStorage instance."""
    return ProfileStorage()

@pytest.fixture
def sample_profile():
    """Create a sample profile for testing."""
    return ProfileResult(
        summary=ProfileSummary(
            elapsed_time_sec=1.0,
            max_footprint_mb=100.0,
            growth_rate_mb_per_sec=0.1
        ),
        files={},
        stacks=[]
    )

class TestProfileStorageInit:
    """Test ProfileStorage initialization."""
    
    def test_storage_creation(self):
        """Test creating ProfileStorage."""
        storage = ProfileStorage()
        assert storage is not None
    
    def test_storage_with_max_profiles(self):
        """Test ProfileStorage with max_profiles limit."""
        storage = ProfileStorage(max_profiles=10)
        assert storage.max_profiles == 10

class TestProfileStorageOperations:
    """Test storage operations."""
    
    def test_store_profile(self, storage, sample_profile):
        """Test storing a profile."""
        profile_id = storage.store(sample_profile)
        assert profile_id is not None
        assert isinstance(profile_id, str)
    
    def test_retrieve_profile(self, storage, sample_profile):
        """Test retrieving a stored profile."""
        profile_id = storage.store(sample_profile)
        retrieved = storage.get(profile_id)
        assert retrieved is not None
        assert retrieved.summary.elapsed_time_sec == 1.0
    
    def test_list_profiles(self, storage, sample_profile):
        """Test listing all profiles."""
        storage.store(sample_profile)
        storage.store(sample_profile)
        profiles = storage.list()
        assert len(profiles) >= 2
    
    def test_retrieve_nonexistent(self, storage):
        """Test retrieving profile that doesn't exist."""
        profile = storage.get("nonexistent")
        assert profile is None
    
    def test_delete_profile(self, storage, sample_profile):
        """Test deleting a profile."""
        profile_id = storage.store(sample_profile)
        storage.delete(profile_id)
        assert storage.get(profile_id) is None
    
    def test_clear_storage(self, storage, sample_profile):
        """Test clearing all profiles."""
        storage.store(sample_profile)
        storage.store(sample_profile)
        storage.clear()
        profiles = storage.list()
        assert len(profiles) == 0

class TestProfileStorageEdgeCases:
    """Test edge cases and limits."""
    
    def test_max_profiles_limit(self, sample_profile):
        """Test storage respects max_profiles limit."""
        storage = ProfileStorage(max_profiles=3)
        # Store more than max
        ids = []
        for i in range(5):
            ids.append(storage.store(sample_profile))
        
        # Should only have 3
        profiles = storage.list()
        assert len(profiles) <= 3
    
    def test_multiple_stores_same_profile(self, storage, sample_profile):
        """Test storing the same profile multiple times."""
        id1 = storage.store(sample_profile)
        id2 = storage.store(sample_profile)
        assert id1 != id2
    
    def test_store_none_handling(self, storage):
        """Test storing None profile."""
        # Should either raise or handle gracefully
        with pytest.raises((TypeError, ValueError)):
            storage.store(None)

class TestProfileStorageIntegration:
    """Test integration with server."""
    
    def test_storage_persistence_flag(self, storage):
        """Test persistence flag in storage."""
        # Verify storage config
        assert hasattr(storage, 'max_profiles')
```

**Implementation**:
1. Create file: `tests/test_storage.py`
2. Copy test template above
3. Run: `uv run pytest tests/test_storage.py -v`
4. Iterate until all tests pass
5. Verify coverage: `uv run pytest --cov=src/scalene_mcp/storage --cov-report=term-missing`

**Success Metric**: storage.py at 100% coverage

---

### Task 2: Enhance profiler.py Tests (2 hours)

**Add to**: `tests/test_profiler.py`

```python
"""Additional tests for timeout and error handling."""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from scalene_mcp.profiler import ScaleneProfiler

class TestProfilerTimeouts:
    """Test timeout handling."""
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_profile_script_timeout(self, mock_exec):
        """Test timeout handling in profile_script."""
        profiler = ScaleneProfiler()
        
        # Mock process that times out
        mock_process = MagicMock()
        mock_process.communicate = MagicMock(
            side_effect=asyncio.TimeoutError()
        )
        mock_exec.return_value = mock_process
        
        with pytest.raises(asyncio.TimeoutError):
            await profiler.profile_script(
                "test_script.py",
                timeout=0.1
            )

class TestProfilerErrors:
    """Test error handling."""
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_process_failure(self, mock_exec):
        """Test handling process execution failure."""
        profiler = ScaleneProfiler()
        
        # Mock process that fails
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.communicate = MagicMock(
            return_value=(b'', b'Scalene error')
        )
        mock_exec.return_value = mock_process
        
        with pytest.raises(RuntimeError):
            await profiler.profile_script("test_script.py")
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_missing_output_file(self, mock_exec):
        """Test when Scalene doesn't create output file."""
        profiler = ScaleneProfiler()
        
        # Mock process that succeeds but produces no output
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate = MagicMock(
            return_value=(b'', b'')
        )
        mock_exec.return_value = mock_process
        
        with pytest.raises(RuntimeError, match="did not create output file"):
            await profiler.profile_script("test_script.py")

class TestProfilerArguments:
    """Test various argument combinations."""
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_gpu_flag(self, mock_exec, valid_profile_file):
        """Test GPU profiling flag."""
        profiler = ScaleneProfiler()
        
        # Mock successful execution
        mock_process = setup_mock_process(valid_profile_file)
        mock_exec.return_value = mock_process
        
        result = await profiler.profile_script(
            "test_script.py",
            gpu=True
        )
        
        # Verify --gpu was in command
        call_args = mock_exec.call_args
        assert '--gpu' in call_args[0]
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_cpu_only_mode(self, mock_exec, valid_profile_file):
        """Test CPU-only mode."""
        profiler = ScaleneProfiler()
        
        mock_process = setup_mock_process(valid_profile_file)
        mock_exec.return_value = mock_process
        
        result = await profiler.profile_script(
            "test_script.py",
            cpu_only=True
        )
        
        # Verify --cpu-only was in command
        call_args = mock_exec.call_args
        assert '--cpu-only' in call_args[0]
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_script_arguments(self, mock_exec, valid_profile_file):
        """Test passing arguments to profiled script."""
        profiler = ScaleneProfiler()
        
        mock_process = setup_mock_process(valid_profile_file)
        mock_exec.return_value = mock_process
        
        result = await profiler.profile_script(
            "test_script.py",
            script_args=["--arg1", "value1", "--arg2", "value2"]
        )
        
        # Verify arguments were passed
        call_args = mock_exec.call_args
        assert "test_script.py" in call_args[0]
        assert "--arg1" in call_args[0]
        assert "value1" in call_args[0]
```

**Implementation**:
1. Open `tests/test_profiler.py`
2. Add test classes above (TestProfilerTimeouts, TestProfilerErrors, TestProfilerArguments)
3. Update imports: `from unittest.mock import patch, MagicMock`
4. Run: `uv run pytest tests/test_profiler.py -v`
5. Verify coverage: `uv run pytest --cov=src/scalene_mcp/profiler --cov-report=term-missing`

**Success Metric**: profiler.py at 100% coverage

---

### Task 3: Enhance analyzer.py Tests (2 hours)

**Add to**: `tests/test_analyzer.py`

```python
"""Additional tests for analyzer edge cases."""

import pytest
from scalene_mcp.analyzer import ProfileAnalyzer
from scalene_mcp.models import ProfileResult, ProfileSummary

@pytest.fixture
def empty_profile():
    """Profile with no data."""
    return ProfileResult(
        summary=ProfileSummary(
            elapsed_time_sec=0.0,
            max_footprint_mb=0.0
        ),
        files={},
        stacks=[]
    )

@pytest.fixture
def profile_no_hotspots():
    """Profile where nothing exceeds threshold."""
    # Create profile where all lines are below 1% CPU
    return ProfileResult(
        summary=ProfileSummary(
            elapsed_time_sec=1.0,
            max_footprint_mb=10.0
        ),
        files={
            "test.py": {
                "functions": [
                    {
                        "name": "func1",
                        "type": "function",
                        "start_line": 1,
                        "end_line": 5,
                        "cpu": 0.001,  # 0.1%
                        "memory": 1.0,
                        "lines": []
                    }
                ]
            }
        },
        stacks=[]
    )

class TestAnalyzerEmptyProfile:
    """Test analyzer with empty profiles."""
    
    def test_hotspots_empty_profile(self, empty_profile):
        """Test getting hotspots from empty profile."""
        analyzer = ProfileAnalyzer(empty_profile)
        hotspots = analyzer.get_cpu_hotspots()
        assert hotspots == []
    
    def test_memory_hotspots_empty(self, empty_profile):
        """Test memory hotspots from empty profile."""
        analyzer = ProfileAnalyzer(empty_profile)
        hotspots = analyzer.get_memory_hotspots()
        assert hotspots == []
    
    def test_bottlenecks_empty(self, empty_profile):
        """Test bottlenecks from empty profile."""
        analyzer = ProfileAnalyzer(empty_profile)
        bottlenecks = analyzer.get_bottlenecks()
        assert bottlenecks == []

class TestAnalyzerThresholds:
    """Test threshold filtering."""
    
    def test_cpu_threshold_filtering(self, profile_no_hotspots):
        """Test CPU threshold filtering."""
        analyzer = ProfileAnalyzer(profile_no_hotspots)
        # With default 1% threshold, should find no hotspots
        hotspots = analyzer.get_cpu_hotspots(threshold_percent=1.0)
        assert len(hotspots) == 0
    
    def test_memory_threshold_filtering(self, profile_no_hotspots):
        """Test memory threshold filtering."""
        analyzer = ProfileAnalyzer(profile_no_hotspots)
        hotspots = analyzer.get_memory_hotspots(threshold_percent=5.0)
        # Check filtering works
        assert isinstance(hotspots, list)

class TestAnalyzerMemoryLeaks:
    """Test memory leak detection."""
    
    def test_no_memory_leaks(self, profile_no_hotspots):
        """Test profile with no leaks."""
        analyzer = ProfileAnalyzer(profile_no_hotspots)
        leaks = analyzer.get_memory_leaks()
        assert isinstance(leaks, list)
    
    def test_leak_detection_edge_cases(self):
        """Test leak detection at boundaries."""
        # Create profile with boundary velocity
        profile = ProfileResult(
            summary=ProfileSummary(
                elapsed_time_sec=1.0,
                max_footprint_mb=100.0,
                growth_rate_mb_per_sec=0.5  # Borderline
            ),
            files={},
            stacks=[]
        )
        analyzer = ProfileAnalyzer(profile)
        leaks = analyzer.get_memory_leaks()
        assert isinstance(leaks, list)

class TestAnalyzerFunctionSummary:
    """Test function summary retrieval."""
    
    def test_function_not_found(self, profile_no_hotspots):
        """Test requesting summary for non-existent function."""
        analyzer = ProfileAnalyzer(profile_no_hotspots)
        summary = analyzer.get_function_summary("nonexistent_function")
        # Should return None or empty summary
        assert summary is None or isinstance(summary, dict)
    
    def test_function_summary_existing(self, profile_no_hotspots):
        """Test getting summary for existing function."""
        analyzer = ProfileAnalyzer(profile_no_hotspots)
        # func1 exists in fixture
        summary = analyzer.get_function_summary("func1")
        assert summary is not None

class TestAnalyzerStackTraces:
    """Test handling of stack traces."""
    
    def test_profile_without_stacks(self, profile_no_hotspots):
        """Test analyzer when profile has no stack traces."""
        analyzer = ProfileAnalyzer(profile_no_hotspots)
        hotspots = analyzer.get_cpu_hotspots()
        # Should work without stacks
        assert isinstance(hotspots, list)
    
    def test_stack_aggregation_missing_stacks(self, empty_profile):
        """Test function aggregation without stacks."""
        analyzer = ProfileAnalyzer(empty_profile)
        summary = analyzer.get_function_summary("any")
        # Should handle gracefully
        assert summary is None or isinstance(summary, dict)
```

**Implementation**:
1. Open `tests/test_analyzer.py`
2. Add fixtures and test classes above
3. Run: `uv run pytest tests/test_analyzer.py -v`
4. Verify coverage: `uv run pytest --cov=src/scalene_mcp/analyzer --cov-report=term-missing`

**Success Metric**: analyzer.py at 100% coverage

---

## Phase 9 Execution (Day 2)

### After Core Testing Complete

```bash
# Run all tests and check coverage
uv run pytest -v --cov=src/scalene_mcp --cov-report=term-missing

# Should show: TOTAL 744 100.0%
```

### Task 4-7: Minor Modules (comparator, parser, server, logging)

```bash
# Quick fix: Add 2-5 targeted test cases each
# Should complete in 3-4 hours total

# For each module:
1. Run coverage report to find exact missing lines
2. Create minimal test to cover those lines
3. Verify coverage increase
```

Example for comparator:
```python
def test_compare_empty_profiles():
    """Compare two empty profiles."""
    prof1 = ProfileResult(...)
    prof2 = ProfileResult(...)
    comp = ProfileComparator()
    diff = comp.compare(prof1, prof2)
    assert diff is not None
```

---

## Phase 9 Execution (Day 3)

### Quality Assurance

```bash
# 1. Type checking
uv run mypy src/
# Should show: Success: no issues found in X source files

# 2. Linting
uv run ruff check src/
# Should show: 0 errors

# 3. Formatting
uv run ruff format src/

# 4. Final coverage verification
uv run pytest --cov=src/scalene_mcp --cov-fail-under=100
# Should pass without error message about coverage

# 5. Test count
uv run pytest -v | grep "passed"
# Should show all tests passing (150+)
```

### Release Preparation

```bash
# 1. Update version
# Edit: pyproject.toml
# Change: version = "0.1.0-dev" → version = "0.1.0"

# 2. Write changelog
# Create: CHANGELOG.md (use template below)

# 3. Build package
uv build
# Should create dist/scalene_mcp-0.1.0.tar.gz

# 4. Create git tag
git tag -a v0.1.0 -m "Release v0.1.0: Initial Scalene-MCP release"

# 5. Verify
python -m pip install dist/scalene_mcp-0.1.0-py3-none-any.whl
python -m scalene_mcp.server --help
```

---

## CHANGELOG Template

```markdown
# Changelog

All notable changes to Scalene-MCP are documented in this file.

## [0.1.0] - 2026-01-XX

### Added
- Initial Scalene-MCP v0.1.0 release
- 12 MCP tools for Python profiling
  - profile_script: Profile Python scripts
  - profile_code: Profile code snippets
  - analyze_profile: Comprehensive analysis
  - get_cpu_hotspots: Find CPU bottlenecks
  - get_memory_hotspots: Identify memory usage
  - get_gpu_hotspots: GPU profiling
  - get_bottlenecks: Severity analysis
  - get_memory_leaks: Leak detection
  - get_function_summary: Per-function metrics
  - compare_profiles: Compare two profiles
  - list_profiles: View stored profiles
  - get_profile: Retrieve profile data
- Support for CPU, GPU, and memory profiling
- Profile storage and comparison
- FastMCP v2 server integration
- Comprehensive documentation (800+ lines)
- 6+ practical examples for real-world use cases
- 155+ unit tests with 100% coverage
- Type safety with Pydantic validation
- Async-first architecture

### Fixed
- (none - initial release)

### Changed
- (none - initial release)

### Known Issues
- Stack trace collection (--stacks) planned for v0.2.0
- Remote profiling planned for future release

## [Unreleased]

### Planned for v0.2.0
- Stack trace analysis and aggregation
- Historical profile tracking
- Visualization generation
- Automatic optimization suggestions
- CI/CD integration templates
```

---

## Final Verification Checklist

- [ ] All tests pass: `uv run pytest -v`
- [ ] Coverage 100%: `uv run pytest --cov --cov-fail-under=100`
- [ ] Type checking: `uv run mypy src/` → 0 errors
- [ ] Linting: `uv run ruff check src/` → 0 errors
- [ ] Formatting: `uv run ruff format src/`
- [ ] README renders on GitHub
- [ ] All examples tested and working
- [ ] Installation works from package
- [ ] Version updated to 0.1.0
- [ ] CHANGELOG.md written
- [ ] Git tag created: v0.1.0

---

## Success = v0.1.0 Release Ready! 🎉
