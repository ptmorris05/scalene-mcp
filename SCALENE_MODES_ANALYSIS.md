# Scalene Usage Modes - Coverage Analysis

## Overview

Scalene supports multiple usage modes. Let's evaluate which ones are supported by Scalene-MCP.

## Usage Modes

### 1. ✅ Single Scripts
**Scalene**: `scalene your_script.py`  
**Scalene-MCP**: Fully supported via `profile_script()`

```python
result = await profiler.profile_script("fibonacci.py")
```

**Status**: ✅ Complete

---

### 2. ✅ Whole Packages/Applications
**Scalene**: `scalene main_app.py` or `python -m scalene my_package.cli_module`  
**Scalene-MCP**: Supported via `profile_script()`

```python
# Profile a package entry point
result = await profiler.profile_script("main_app.py")

# Profile a module entry point
result = await profiler.profile_script("my_package/cli_module.py")
```

**Status**: ✅ Complete

---

### 3. ✅ Commands with Arguments
**Scalene**: `python -m scalene your_script.py --arg value`  
**Scalene-MCP**: Supported via `script_args` parameter

```python
result = await profiler.profile_script(
    "app.py",
    script_args=["--debug", "--output", "results.json"]
)
```

**Status**: ✅ Complete

---

### 4. ❌ Programmatic Control (In-Code Profiling)
**Scalene**: Direct API via `scalene_profiler.start()` and `stop()`

```python
from scalene.scalene_profiler import Scalene

Scalene.start()
# ... code to profile ...
Scalene.stop()
```

**Scalene-MCP**: NOT currently supported  
**Limitation**: Uses subprocess-based profiling only

**Status**: ❌ Missing

---

### 5. ❌ Process Attachment (Runtime Profiling)
**Scalene**: `python -m scalene --pid <PID>` (attach to running process)

**Scalene-MCP**: NOT currently supported  
**Limitation**: Cannot attach to existing processes

**Status**: ❌ Missing

---

## Gap Analysis

### Currently Supported (3/5)
- ✅ Single scripts
- ✅ Packages/applications
- ✅ Commands with arguments

### Not Supported (2/5)
- ❌ Programmatic control (`Scalene.start()`/`stop()`)
- ❌ Process attachment (`--pid` flag)

---

## Why These Gaps Exist

### Subprocess Design Choice
The current implementation uses `python -m scalene run` via subprocess because:
1. **Reliability**: Subprocess output is isolated and clean
2. **Simplicity**: Don't need to manage Scalene's internal state
3. **Safety**: Script crashes don't crash the profiler
4. **Resource cleanup**: Automatic process termination

### Programmatic API Limitations
Using Scalene's programmatic API (`Scalene.start()`/`stop()`) would require:
1. Sharing Python interpreter with script
2. Managing Scalene's internal state within same process
3. Handling threading/async within the profiler
4. More complex error recovery

### Process Attachment Limitations
Runtime process profiling (`--pid`) requires:
1. System-level process management
2. Potentially elevated permissions
3. Complex IPC mechanisms
4. OS-specific implementations

---

## Enhancement Recommendations

### Tier 1: High Value (For Phase 8-9)

#### Add Programmatic Profiling Method
```python
class ScaleneProfiler:
    async def profile_function(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> ProfileResult:
        """Profile a single function call.
        
        Args:
            func: Function to profile
            *args: Positional arguments to pass to function
            **kwargs: Keyword arguments to pass to function
            
        Returns:
            ProfileResult with profiling data
        """
        # Use Scalene's API directly for in-process profiling
        from scalene.scalene_profiler import Scalene
        
        Scalene.start()
        try:
            result = func(*args, **kwargs)
        finally:
            Scalene.stop()
        
        # Parse and return profile
        return self._parse_profile()
```

**Benefits**:
- Profile individual functions without file I/O
- Better for LLM-driven profiling workflows
- Lower latency for quick analysis
- Direct integration with Python code

**Tradeoffs**:
- Adds dependency on Scalene's internal API
- Requires same-process execution
- More error handling complexity

---

### Tier 2: Medium Value (For future versions)

#### Add Context Manager Support
```python
class ScaleneProfiler:
    @contextmanager
    async def profile_context(self, label: str = ""):
        """Profile code block with context manager.
        
        Usage:
            async with profiler.profile_context("preprocessing"):
                # code to profile
                pass
        """
        # Start profiling
        # Yield control
        # Stop and parse results
```

---

### Tier 3: Lower Value (Future consideration)

#### Process Attachment
```python
async def profile_process(
    self,
    pid: int,
    duration: float
) -> ProfileResult:
    """Attach to and profile a running process.
    
    Args:
        pid: Process ID to profile
        duration: How long to profile for (seconds)
    """
```

**Complexity**: High (OS-specific, permissions, etc.)  
**Value**: Lower (niche use case for most LLM workflows)

---

## Impact on MCP Tools

### Current Tools (Complete for subprocess model)
All 12 tools work well with subprocess-based profiling:
- `profile_script` ✅
- `profile_code` ✅
- Analysis tools ✅
- Comparison tools ✅

### New Tools Needed (For programmatic support)
Could add:
- `profile_function` - Profile individual functions
- `profile_with_context` - Profile named code blocks
- `profile_code_advanced` - In-process code profiling

---

## Recommendation

### For Phase 7 (Documentation)
✅ **Document the current scope clearly**:
- Explain subprocess-based approach
- List supported use cases
- Explain why certain modes aren't supported
- Provide workarounds when possible

### For Phase 8-9 (Enhancement)
⏳ **Consider adding**:
1. Programmatic profiling via `profile_function()`
2. Context manager support for code blocks
3. Updated documentation with expanded examples

### For Future (v1.1+)
🔮 **Potential additions**:
1. Direct Scalene API integration
2. Hybrid profiling (subprocess + programmatic)
3. Process attachment for special cases

---

## Current Scope Summary

**Scalene-MCP is optimized for**:
- Profiling complete Python scripts
- LLM-based workflow integration
- Reproducible, isolated profiling
- Clean error handling and resource cleanup

**Scalene-MCP is NOT designed for**:
- In-process function-level profiling
- Real-time process attachment
- Complex profiling state management

**This is intentional and appropriate for**:
- LLM use cases (scripts, not function-level)
- Production reliability (isolated subprocess)
- Ease of implementation and debugging

---

## Summary Table

| Use Case | Support | Via | Notes |
|----------|---------|-----|-------|
| Scripts | ✅ | `profile_script()` | Full support |
| Packages | ✅ | `profile_script()` | Entry point path |
| With Args | ✅ | `script_args` param | Pass args directly |
| In-Code Start/Stop | ❌ | Not implemented | Would require API direct |
| Process Attach | ❌ | Not implemented | Would require --pid support |

---

## Conclusion

Scalene-MCP supports **3 out of 5** major Scalene usage modes. The two gaps (programmatic control and process attachment) represent lower priority use cases for LLM-based code analysis workflows.

**Recommendation for documentation**: Clearly explain what's supported and why the subprocess approach was chosen, with notes on potential future enhancements.