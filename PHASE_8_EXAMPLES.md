# Phase 8: Practical Examples & Real-World Use Cases

## Overview

Phase 8 provides production-ready examples that show how developers actually use Scalene-MCP to write faster Python code.

**Key Principle**: Practical, low-resource examples that run quickly while demonstrating real optimization patterns.

---

## Target Audience

Who uses Scalene-MCP?

### 1. **Data Scientists & ML Engineers**
- Optimizing data pipelines
- Finding bottlenecks in data processing
- Comparing algorithm implementations
- Profiling ML model training

### 2. **Backend/Web Developers**
- Identifying bottlenecks in API servers
- Detecting memory leaks in long-running services
- Comparing database query patterns
- Optimizing endpoint performance

### 3. **Library Maintainers**
- Benchmarking performance
- Ensuring API efficiency
- Comparing implementation strategies
- Release performance validation

### 4. **Systems Programmers**
- Profiling C/C++/Rust bindings
- Understanding Python vs native time
- Finding CPU bottlenecks
- Memory optimization

### 5. **Game Developers**
- Profiling game engines built in Python
- Finding frame-time bottlenecks
- Memory management verification

---

## Example Structure

All examples follow this pattern:

1. **Real-world scenario** - What problem is this solving?
2. **Code implementation** - The actual code to profile
3. **Why it matters** - What should developers look for?
4. **Scalene-MCP integration** - How to use our tools
5. **Expected insights** - What you should find

---

## Example 1: Data Processing Pipeline Optimization

**File**: `1_data_processing_pipeline.py`

**Real-world scenario**: 
A data scientist has a data processing pipeline that's slow. They suspect using loops (slow) instead of vectorized operations is the problem.

**What Scalene shows**:
- Line-by-line Python time
- Where loops are expensive
- NumPy vectorized operations are fast (C implementation)

**Who cares**:
- Data scientists working with datasets
- ETL engineers
- ML feature engineers
- Anyone processing data with NumPy/arrays

**Optimization insight**:
```
BEFORE (slow):
  - Python time high (loops)
  - Many function calls

AFTER (fast):
  - More C time (NumPy)
  - Fewer function calls
```

**Dependencies**: numpy only

**Run it**:
```bash
# Profile the slow version
python -m scalene examples/1_data_processing_pipeline.py

# Expected: ~0.1s with clear Python vs C time difference
```

---

## Example 2: Algorithm Comparison

**File**: `2_algorithm_comparison.py`

**Real-world scenario**:
Implementing a feature and choosing between multiple algorithms (bubble sort vs quicksort vs Python's builtin).

**What Scalene shows**:
- CPU time for each algorithm
- Call stack depth (bubble sort does more function calls)
- Python's sorted() (C/Timsort) is fastest

**Who cares**:
- Algorithm engineers
- Library designers
- Anyone choosing implementation strategies

**Expected insights**:
```
Algorithm A (Bubble Sort O(n²)):  ~50% Python time
Algorithm B (Quick Sort O(n log n)):  ~30% Python time  
Algorithm C (Python sorted C/Timsort):  ~5% Python time
```

**Run it**:
```bash
python -m scalene examples/2_algorithm_comparison.py

# Profile to see actual time distribution
```

---

## Example 3: C Bindings Profiling

**File**: `3_c_bindings_profiling.py`

**Real-world scenario**:
Understanding whether performance is limited by Python code or C extension libraries.

**Key insight**: Scalene separates Python time from C time

```
Scalene Output shows:
  - Python time (Python loops, function calls)
  - C time (NumPy and other C extensions)
  - System time (I/O, system calls)
```

**What this teaches**:
- Where C bindings appear
- How much time is in each layer
- Where to focus optimization

**Example breakdown**:
```
Pure Python loop:          → Python time
NumPy operations:          → C time
NumPy math (sin, exp):     → C time
```

**Why this matters**:
If 80% of time is C time, you need to use different C libraries or reshape your problem. If 80% is Python time, you can optimize the Python code or use vectorization.

**Dependencies**: numpy only

**Run it**:
```bash
python -m scalene examples/3_c_bindings_profiling.py

# Look at the Python vs C breakdown
```

---

## Example 4: Memory Leak Detection

**File**: `4_memory_leak_detection.py`

**Real-world scenario**:
A web service slowly consumes memory over time. You need to find where the leak is.

**What Scalene shows**:
- Memory allocation per line
- Allocation velocity (MB/second)
- Confidence score for leak detection

**Leak detection algorithm**:
```
Lines with HIGH allocation velocity = Likely leaks
Lines with LOW velocity = Normal allocation pattern
```

**Example pattern**:
```python
cache = {}  # Global cache
for i in range(1000):
    cache[f"key_{i}"] = data * 1000  # High velocity leak
```

**Run it**:
```bash
python -m scalene --memory examples/4_memory_leak_detection.py

# Look for lines with high allocation velocity
```

---

## Example 5: I/O Bound Code Profiling

**File**: `5_io_bound_profiling.py`

**Real-world scenario**:
A web scraper waits for network responses. You want to see time spent waiting vs processing.

**What Scalene shows**:
- System time (I/O waiting)
- Python time (processing)
- Time spent where

**Optimization insight**:
```
High system time:      → Use async/parallel requests
High Python time:      → Optimize processing logic
High C time:           → Use better C libraries
```

**Example scenario**:
- Sequential API calls: Each call waits (high system time)
- Batch processing: Multiple calls in parallel
- Async/await: True concurrency

**Run it**:
```bash
python -m scalene examples/5_io_bound_profiling.py

# See system time from time.sleep() and file I/O
```

---

## Example 6: GPU Profiling

**File**: `6_gpu_profiling.py`

**Note**: GPU support is optional. This example shows the pattern without requiring GPU.

**Real-world scenario**:
A machine learning engineer wants to understand CPU vs GPU time split.

**What Scalene shows** (with GPU hardware):
- CPU time
- GPU time
- Data transfer overhead

**When to use GPU profiling**:
- Training deep learning models
- Running inference with GPU acceleration
- Large matrix operations
- Scientific computing

**Optimization insight**:
```
GPU underutilized:     → Move more computation to GPU
High data transfer:    → Optimize batch sizes
Bottleneck on CPU:     → Use GPU-accelerated libraries
```

**Pattern for PyTorch** (if you have GPU):
```python
# CPU computation
tensor_cpu = torch.randn(1000, 1000)
result_cpu = torch.mm(tensor_cpu, tensor_cpu)

# GPU computation
tensor_gpu = torch.randn(1000, 1000, device='cuda')
result_gpu = torch.mm(tensor_gpu, tensor_gpu)

# Profile with: python -m scalene --gpu your_script.py
```

---

## Running Examples with Scalene-MCP

### Quick Profile
```bash
# Basic profiling
python -m scalene examples/1_data_processing_pipeline.py
```

### With Memory Profiling
```bash
# See memory usage
python -m scalene --memory examples/4_memory_leak_detection.py
```

### With All Options
```bash
# CPU, memory, and GPU (if available)
python -m scalene --memory --gpu examples/3_c_bindings_profiling.py
```

### Using Scalene-MCP Tools
```python
from scalene_mcp.profiler import ScaleneProfiler
import asyncio

async def main():
    profiler = ScaleneProfiler()
    
    # Profile the script
    result = await profiler.profile_script(
        "examples/1_data_processing_pipeline.py",
        cpu=True,
        memory=True,
        gpu=False
    )
    
    # Analyze
    from scalene_mcp.analyzer import ProfileAnalyzer
    analyzer = ProfileAnalyzer()
    
    hotspots = analyzer.get_hotspots(result, metric="cpu", limit=5)
    print("Top CPU hotspots:")
    for spot in hotspots:
        print(f"  {spot.file}:{spot.line} - {spot.time_sec:.2f}s")

asyncio.run(main())
```

---

## Expected Output Examples

### Example 1 Output
```
Scalene profiling results:
  Line 28: slow_python_processing() - 2.5 seconds (85% Python time)
  Line 35: df.iterrows() - 2.3 seconds (95% Python time)
  
Recommendation: Use vectorized operations instead of iterrows()
```

### Example 3 Output
```
Python vs C Time Breakdown:
  pure_python_sum()     - 0.1s Python time
  numpy_sum()           - 0.05s C time  (60% faster!)
  pandas operations     - 0.08s C time  (various operations)
  
Insight: NumPy operations are 60% faster due to C implementation
```

### Example 4 Output
```
Memory Leak Detection:
  Line 18: cache[key] = data
    Velocity: 0.5 MB/sec  (HIGH - likely leak)
    Confidence: MEDIUM
    
  Line 25: del results[key]
    Velocity: -0.05 MB/sec (cleanup, good!)
    Confidence: LOW
```

---

## Choosing Which Example to Run

**I have a slow data pipeline**
→ Run Example 1: Data Processing Pipeline

**I'm choosing between algorithms**
→ Run Example 2: Algorithm Comparison

**I'm using NumPy/Pandas/C libraries**
→ Run Example 3: C Bindings Profiling

**My service uses too much memory**
→ Run Example 4: Memory Leak Detection

**My code waits for network/I/O**
→ Run Example 5: I/O Bound Profiling

**I'm training ML models**
→ Run Example 6: GPU Profiling

---

## Performance Characteristics

All examples are designed to be quick and have minimal dependencies:

| Example | Runtime | Dependencies | Purpose |
|---------|---------|--------------|---------|
| 1 | ~0.1 seconds | numpy | Data processing pipeline |
| 2 | ~0.1 seconds | None | Algorithm comparison |
| 3 | ~0.1 seconds | numpy | C bindings profiling |
| 4 | ~0.04 seconds | None | Memory leak detection |
| 5 | ~0.2 seconds | None | I/O bound profiling |
| 6 | ~0.1 seconds | None | GPU pattern demo |

**Total run time**: < 1 second for all examples

**Minimal dependencies**: Only Example 1 and 3 need numpy (lightweight, widely available)

---

## Next Steps After Profiling

### If You Find Hotspots
1. Use `get_bottlenecks()` to see severity
2. Read the code at that line
3. Check if it's Python time (can optimize) or C time (use better library)

### If You Find Memory Issues
1. Use `get_memory_leaks()` to see allocation velocity
2. Check lines with high velocity
3. Add explicit cleanup or use context managers

### If You Find I/O Bottlenecks
1. Look for `time.sleep()` and file operations
2. Consider async/parallel processing
3. Batch requests instead of sequential

### If You Find GPU Underutilization
1. Move more computation to GPU
2. Reduce CPU-GPU data transfer
3. Use GPU-optimized algorithms

---

## Integration with LLM Workflows

These examples show how an LLM-powered development tool would use Scalene-MCP:

**Developer**: "My data pipeline is slow, help me optimize it"

**LLM with Scalene-MCP**:
1. Profile the code with `profile_script()`
2. Analyze with `get_hotspots()` and `get_bottlenecks()`
3. Identify root cause (loops vs C bindings?)
4. Suggest specific optimizations

---

## Running Tests on Examples

All examples can be tested without GPU:
```bash
# Test all examples
for i in 1 2 3 4 5 6; do
    echo "Testing example $i..."
    python -m scalene examples/${i}_*.py
done
```

GPU examples gracefully degrade to CPU (see Example 6 pattern).

---

## Future Enhancement Ideas

### Phase 9
- Add more specialized examples (web frameworks, async, etc.)
- Add before/after optimization examples
- Create benchmark comparison suite

### Phase 10
- Real-world library examples (requests, FastAPI, etc.)
- Performance regression detection examples
- Continuous profiling patterns

---

## See Also

- [API Reference](../docs/api.md) - All available tools
- [Architecture](../docs/architecture.md) - How it works
- [Troubleshooting](../docs/troubleshooting.md) - Common issues
- [README](../README.md) - Quick start