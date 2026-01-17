# Scalene MCP Tools Reference

Quick reference for all tools provided by the Scalene MCP Server.

## Discovery Tools

These help the LLM understand your project context.

### `get_project_root()`

Get the detected project root and structure type.

**Returns:**
```json
{
  "root": "/absolute/path/to/project",
  "type": "python|node|mixed|unknown",
  "markers_found": "pyproject.toml, .git, setup.py"
}
```

**Use when:** LLM needs to understand your project structure.

---

### `list_project_files(pattern="*.py", max_depth=3, exclude_patterns="...")`

List project files matching a glob pattern.

**Parameters:**
- `pattern`: Glob pattern like `*.py`, `src/**/*.py`, `tests/**`
- `max_depth`: Maximum directory depth to search (default: 3)
- `exclude_patterns`: Comma-separated patterns to skip (`.git`, `__pycache__`, etc.)

**Returns:**
```json
[
  "src/main.py",
  "src/utils.py",
  "tests/test_main.py"
]
```

**Use when:** Finding files to profile or understanding project structure.

---

### `set_project_context(project_root)`

Explicitly set project root (overrides auto-detection).

**Parameters:**
- `project_root`: Absolute path to project directory

**Returns:**
```json
{
  "project_root": "/path/to/project",
  "status": "set"
}
```

**Use when:** Auto-detection fails or you want to override it.

---

## Profiling Tools

### `profile_script(script_path, cpu_only=False, include_memory=True, include_gpu=False, ...)`

Profile a standalone Python script.

**Parameters:**
- `script_path`: Path to script (relative or absolute)
- `cpu_only`: Skip memory/GPU profiling
- `include_memory`: Profile memory allocations (default: true)
- `include_gpu`: Profile GPU usage, requires NVIDIA CUDA
- `reduced_profile`: Show only lines >1% CPU or >100 allocations
- `profile_only`: Comma-separated paths to profile (e.g., "myapp,src")
- `profile_exclude`: Comma-separated paths to skip (e.g., "tests,vendor")
- `script_args`: Command-line arguments for the script

**Returns:**
```json
{
  "profile_id": "profile_0",
  "summary": {
    "total_cpu_percent": 100.0,
    "total_memory_mb": 256.5,
    "runtime_seconds": 5.23
  },
  "text_summary": "..."
}
```

**Example:**
```
profile_script("main.py")
profile_script("src/train.py", include_gpu=True, script_args=["--batch-size", "32"])
```

---

### `profile_code(code, cpu_only=False, include_memory=True, reduced_profile=False)`

Profile Python code directly (without file).

**Parameters:**
- `code`: Python code as string
- `cpu_only`: Skip memory profiling
- `include_memory`: Profile memory allocations
- `reduced_profile`: Show only significant lines

**Returns:** Same as `profile_script`

**Example:**
```
profile_code("""
for i in range(1000000):
    x = i * 2
""")
```

---

## Analysis Tools

### `analyze_profile(profile_id, focus="all", top_n=10, cpu_threshold=5.0, memory_threshold_mb=10.0)`

Comprehensive analysis of a profile.

**Parameters:**
- `profile_id`: ID from `profile_script` or `profile_code`
- `focus`: "cpu", "memory", "gpu", or "all"
- `top_n`: Number of items to return
- `cpu_threshold`: Minimum CPU % to report
- `memory_threshold_mb`: Minimum memory to report

**Returns:**
```json
{
  "hotspots": [...],
  "bottlenecks": {...},
  "memory_leaks": [...],
  "recommendations": [...]
}
```

---

### `get_cpu_hotspots(profile_id, top_n=10)`

Get lines using the most CPU time.

**Returns:**
```json
[
  {
    "type": "cpu",
    "filename": "src/compute.py",
    "lineno": 45,
    "line": "    result = expensive_function(data)",
    "cpu_percent": 45.3
  }
]
```

---

### `get_memory_hotspots(profile_id, top_n=10)`

Get lines allocating the most memory.

**Returns:**
```json
[
  {
    "type": "memory",
    "filename": "src/data.py",
    "lineno": 32,
    "line": "    big_list = [x for x in range(1000000)]",
    "memory_mb": 42.5
  }
]
```

---

### `get_gpu_hotspots(profile_id, top_n=10)`

Get lines using the most GPU time (NVIDIA CUDA only).

**Returns:**
```json
[
  {
    "type": "gpu",
    "filename": "src/model.py",
    "lineno": 78,
    "line": "    output = model.forward(input_tensor)",
    "gpu_percent": 89.2
  }
]
```

---

### `get_bottlenecks(profile_id, cpu_threshold=5.0, memory_threshold_mb=10.0)`

Get lines exceeding performance thresholds.

**Returns:**
```json
{
  "cpu": [...lines using >5% CPU...],
  "memory": [...lines allocating >10MB...],
  "gpu": [...lines using >5% GPU...]
}
```

---

### `get_memory_leaks(profile_id)`

Detect potential memory leaks (growing allocations).

**Returns:**
```json
[
  {
    "filename": "src/cache.py",
    "lineno": 15,
    "line": "    cache.append(item)",
    "velocity_mb_per_sec": 2.5,
    "likelihood_pct": 85
  }
]
```

---

### `compare_profiles(before_id, after_id)`

Compare two profiles to measure optimization impact.

**Returns:**
```json
{
  "runtime_change_pct": -25.3,
  "memory_change_pct": -15.2,
  "improvements": [
    "Runtime decreased by 25.3%",
    "Memory usage decreased by 15.2%"
  ],
  "regressions": [],
  "summary_text": "✅ Optimization successful..."
}
```

**Use when:** Validating optimizations after code changes.

---

### `get_file_details(profile_id, filename)`

Get all metrics for a specific file.

**Parameters:**
- `profile_id`: ID from profiling
- `filename`: File name (as it appears in profile)

**Returns:**
```json
{
  "filename": "src/main.py",
  "lines": {
    "45": {
      "line_number": 45,
      "cpu_percent_python": 12.5,
      "cpu_percent_native": 0.0,
      "memory_python_mb": 5.2,
      "memory_native_mb": 0.0,
      "source_code": "    result = compute(data)"
    }
  },
  "total_cpu_percent": 100.0,
  "total_memory_mb": 256.5
}
```

---

### `list_profiles()`

List all profiles captured in this session.

**Returns:**
```json
["profile_0", "profile_1", "profile_2"]
```

**Use when:** Checking available profiles before comparison.

---

### `get_recommendations(profile_id)`

Get actionable optimization suggestions.

**Returns:**
```json
[
  "Line 45 in compute.py: Consider using NumPy vectorization",
  "Memory leak at line 89: Ensure file handles are closed",
  "Line 123: Cache the result instead of recomputing"
]
```

---

### `get_function_summary(profile_id, top_n=10)`

Get function-level performance metrics.

**Returns:**
```json
[
  {
    "function_name": "expensive_function",
    "filename": "src/compute.py",
    "start_line": 40,
    "total_cpu_percent": 45.3,
    "total_memory_mb": 128.5
  }
]
```

**Use when:** High-level view is needed (functions not lines).

---

## Typical Workflows

### Workflow 1: Find and Fix Bottlenecks

1. `profile_script("main.py")` → Get profile_id
2. `get_bottlenecks(profile_id)` → Find issues
3. `get_recommendations(profile_id)` → Get suggestions
4. Fix code
5. `profile_script("main.py")` → Get new profile_id
6. `compare_profiles(old_id, new_id)` → Verify improvement

### Workflow 2: Memory Leak Detection

1. `profile_script("app.py", include_memory=True)` → Profile with memory
2. `get_memory_leaks(profile_id)` → Detect leaks
3. `get_file_details(profile_id, "src/problem_file.py")` → Zoom into file
4. `get_recommendations(profile_id)` → Get fixing advice

### Workflow 3: GPU Optimization

1. `profile_script("train.py", include_gpu=True)` → Profile with GPU
2. `get_gpu_hotspots(profile_id, top_n=5)` → Find GPU bottlenecks
3. `get_function_summary(profile_id, top_n=5)` → Function view
4. `compare_profiles(before, after)` → Measure impact

---

## Notes

- **Relative paths** are resolved from project root (e.g., `"main.py"` → `"/project/root/main.py"`)
- **Absolute paths** are used as-is
- **Project root** is auto-detected but can be set with `set_project_context`
- **Profile IDs** persist in server memory during a session
- **GPU support** requires NVIDIA CUDA and PyTorch/TensorFlow
