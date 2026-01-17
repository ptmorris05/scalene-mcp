# Storage Strategy for scalene-mcp

## Problem Analysis

### Current Approach
- **profiler.py**: Creates temp files for Scalene output, leaves them on disk
- **storage.py**: Persists ProfileResults to ~/.scalene-mcp/profiles/
- **Risks**: Disk clutter, no cleanup, unbounded storage growth

### Why Files Are Necessary
Scalene's design requires file I/O:
1. Scalene CLI needs a file to profile
2. Scalene **always** writes JSON output to a file (no in-memory option)
3. Even using Scalene's Python API (`scalene_profiler.start/stop`), it writes to disk

## Recommended Strategy

### 1. Temporary Files (REQUIRED)
**Purpose**: Scalene requires JSON output files  
**Approach**: Use Python's `tempfile` with auto-cleanup  
**Lifecycle**:
```python
# Create temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=True) as f:
    output_path = f.name
    # Run Scalene, writes to output_path
    # Parse JSON immediately
    profile_result = parser.parse_file(output_path)
# File auto-deleted when context exits
```

**Benefits**:
- Automatic cleanup
- No disk space accumulation
- Secure (files in /tmp with restricted permissions)

### 2. Persistent Storage (OPTIONAL)
**Purpose**: Enable comparison features, historical analysis  
**Approach**: Opt-in parameter, not default  
**Design**:
```python
async def profile_script(
    self,
    script_path: Path,
    *,
    save_profile: bool = False,  # Opt-in
    storage_dir: Path | None = None,
    ...
) -> ProfileResult:
    # Always profile to temp file
    # Parse immediately
    # Only save if save_profile=True
```

**Benefits**:
- User controls when profiles are saved
- Can implement retention policies (max age, max count)
- Clear separation: temporary vs permanent

### 3. In-Memory by Default
**Approach**: Return ProfileResult objects directly  
**MCP Resources**: Use in-memory cache with TTL

```python
# Server maintains in-memory cache
class ProfileCache:
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self._cache: dict[str, tuple[ProfileResult, float]] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds
    
    def get(self, profile_id: str) -> ProfileResult | None:
        if profile_id in self._cache:
            result, timestamp = self._cache[profile_id]
            if time.time() - timestamp < self._ttl:
                return result
            # Expired
            del self._cache[profile_id]
        return None
```

## Implementation Plan

### Phase 1: Fix profiler.py (IMMEDIATE)
- [ ] Use `NamedTemporaryFile` with context manager
- [ ] Parse JSON immediately after profiling
- [ ] Delete temp file automatically
- [ ] Return ProfileResult object directly

### Phase 2: Make storage.py optional (NEXT)
- [ ] Add `save_profile` parameter to profile tools
- [ ] Only use ProfileStorage when explicitly requested
- [ ] Add cleanup utilities (delete old profiles, clear all)

### Phase 3: Add in-memory caching (PHASE 4)
- [ ] Create ProfileCache class
- [ ] Store recent profiles in memory
- [ ] Implement MCP resources backed by cache
- [ ] Add TTL and size limits

### Phase 4: Comparison features (PHASE 5)
- [ ] Compare in-memory profiles first
- [ ] Optionally load from storage
- [ ] User decides what to persist

## Security Considerations

1. **Temp Files**: Use `tempfile.NamedTemporaryFile` (secure by default)
2. **Storage Directory**: Validate paths, prevent directory traversal
3. **Profile Content**: Sanitize file paths in JSON before storage
4. **Permissions**: Restrict storage directory to user only (0700)

## Cleanup Strategy

### Automatic
- Temp files: Auto-deleted by `NamedTemporaryFile`
- In-memory cache: TTL + LRU eviction

### Manual (Add to tools)
```python
@server.tool
async def cleanup_old_profiles(max_age_days: int = 7) -> str:
    """Delete profiles older than N days"""
    
@server.tool
async def clear_profile_cache() -> str:
    """Clear in-memory profile cache"""
```

## File I/O Minimization

### Current: Multiple writes
1. Scalene writes JSON
2. We read JSON
3. We write ProfileResult to storage (storage.py)
4. Later read from storage

### Improved: Single read
1. Scalene writes JSON to temp file
2. We read JSON once
3. Keep in memory
4. Optionally persist if requested

**Savings**: Eliminates 2 I/O operations per profile

## Summary

**Keep**: Temporary files (Scalene requires them)  
**Change**: Make persistent storage opt-in  
**Add**: In-memory caching for recent profiles  
**Result**: Clean, efficient, user-controlled storage
