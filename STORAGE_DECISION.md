# Storage Decision: File I/O Strategy for scalene-mcp

## Question
Should we store profile results to disk? What are the risks and benefits?

## Analysis

### Why Files Are Necessary
Scalene's architecture **requires** file I/O:
1. Scalene CLI needs a Python file to profile
2. Scalene **always** writes JSON output to a file (no in-memory API)
3. Even using `scalene_profiler.start/stop()` API, it writes to disk

**Conclusion**: Temporary files are unavoidable.

### Risks of File Storage
1. **Disk Space**: Unbounded growth without cleanup
2. **Cleanup**: Orphaned temp files if process crashes
3. **Security**: File permissions, malicious content
4. **Permissions**: Write failures in restricted environments
5. **Concurrency**: Multiple processes writing same file

### Benefits of Storage
1. **Comparison**: Compare profiles across time
2. **History**: Track performance trends
3. **Async**: Profile now, analyze later
4. **Sharing**: Share profiles between tools

## Decision: Hybrid Approach

### 1. Temporary Files (REQUIRED)
**Use**: Python's `tempfile.NamedTemporaryFile`  
**Lifecycle**: Create → Profile → Parse → Delete  
**Implementation**:
```python
with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
    output_path = Path(f.name)

try:
    # Run Scalene → writes to output_path
    # Parse JSON immediately
    profile_result = parser.parse_file(output_path)
    return profile_result
finally:
    # Always cleanup
    output_path.unlink(missing_ok=True)
```

**Benefits**:
- Automatic cleanup in finally block
- No accumulation
- Secure default permissions
- Lives in `/tmp` (cleared on reboot)

### 2. Persistent Storage (OPTIONAL)
**Use**: Opt-in parameter for important profiles  
**Lifecycle**: User decides what to save  
**Implementation**:
```python
# Profiling always returns in-memory result
profile_result = await profiler.profile_script(script_path)

# User explicitly saves if needed
if save_for_later:
    storage = ProfileStorage()
    storage.save(profile_result)
```

**When to save**:
- Benchmarks for comparison
- Baseline profiles for CI
- Performance regression tracking
- Historical analysis

**When NOT to save**:
- Ad-hoc profiling
- Quick checks
- Development testing

### 3. In-Memory Cache (FUTURE)
**Use**: Recent profiles for MCP resources  
**Lifecycle**: LRU cache with TTL  
**Implementation**: Later phase (Phase 4)

## Implementation Summary

### What Changed
1. **profiler.py**: 
   - Returns `ProfileResult` directly (not file path)
   - Uses `tempfile.NamedTemporaryFile` with cleanup
   - Parses JSON immediately after profiling
   - Deletes temp file in finally block

2. **storage.py**: 
   - Added docstring explaining optional nature
   - Added `cleanup_old()` and `clear_all()` methods
   - Added file permission restrictions (0700/0600)
   - NOT used by default

3. **server.py** (future):
   - Will keep profiles in-memory by default
   - User can optionally save via parameter
   - MCP resources backed by in-memory cache

### File I/O Comparison

**Before** (hypothetical full-storage approach):
1. Scalene writes JSON → disk
2. Read JSON → parse
3. Write ProfileResult → disk (storage.py)
4. Later: Read from storage → disk
**Total: 2 writes + 2 reads = 4 I/O ops**

**After** (current approach):
1. Scalene writes JSON → disk (temp)
2. Read JSON → parse → in-memory
3. Delete temp file
**Total: 1 write + 1 read + 1 delete = minimal I/O**

**Savings**: 50% fewer I/O operations

### Security Measures
- ✅ Temp files in `/tmp` with restricted permissions
- ✅ Storage directory chmod 0700 (user only)
- ✅ Profile files chmod 0600 (user only)
- ✅ Path validation (prevent directory traversal)
- ✅ Automatic cleanup in finally blocks
- ✅ Cleanup utilities for old profiles

## Recommendations for Usage

### For Users
```python
# Quick profiling - no storage
result = await profiler.profile_script("script.py")

# Important benchmark - save it
result = await profiler.profile_script("script.py")
storage.save(result)  # Explicit opt-in

# Cleanup old profiles
storage.cleanup_old(max_age_days=7)
```

### For CI/CD
```python
# Baseline profiles
storage = ProfileStorage("./baselines")
result = await profiler.profile_script("benchmark.py")
storage.save(result)

# Compare against baseline
baseline = storage.load("previous_run")
comparison = comparator.compare(baseline, result)
```

## Conclusion

**Best Practice**: 
- Minimize file I/O where possible
- Use temp files with auto-cleanup
- Make persistence opt-in
- Provide cleanup utilities

**Result**: Fast, clean, secure, user-controlled storage strategy.
