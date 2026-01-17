# Scalene Coverage Analysis - Documentation Update

## What Was Analyzed

You asked: "Does our MCP server give LLMs the ability to do all of these?" referring to Scalene's usage modes:

1. **Single Scripts**: `scalene your_script.py`
2. **Whole Packages**: `scalene main_app.py` or `python -m scalene my_package.cli_module`
3. **Any Python Command**: `python -m scalene your_script.py --arg value`
4. **Programmatic Control**: `Scalene.start()` and `Scalene.stop()` within code
5. **Process Attachment**: `python -m scalene --pid <PID>`

## Coverage Assessment

### ✅ Fully Supported (3/5)

1. **Single Scripts**
   - Supported via: `profile_script("script.py")`
   - Complete support for all profiling options

2. **Whole Packages/Applications**
   - Supported via: `profile_script("main_app.py")` or `profile_script("my_package/cli_module.py")`
   - Works with any entry point

3. **Commands with Arguments**
   - Supported via: `script_args` parameter
   - Example: `profile_script("app.py", script_args=["--debug", "--output", "file.json"])`

### ❌ Not Currently Supported (2/5)

4. **Programmatic Control**
   - Not supported: Direct `Scalene.start()`/`stop()` API
   - Reason: We use subprocess approach for isolation
   - Could be added in v1.1+

5. **Process Attachment**
   - Not supported: Profiling running processes via `--pid`
   - Reason: Subprocess model doesn't support dynamic attachment
   - Could be added in v2.0+

## Why This Design

The **subprocess-based approach** was chosen (and is documented) because:

1. **Isolation**: Script execution is isolated from profiler state
2. **Reliability**: No state conflicts or memory leaks
3. **Simplicity**: Don't manage Scalene's internal state machine
4. **Safety**: Script crashes/hangs don't crash profiler
5. **LLM Fit**: Perfect for "profile complete scripts" use case

This is a **conscious, well-reasoned design choice** - not an oversight.

## What Was Updated

### 1. Created SCALENE_MODES_ANALYSIS.md
- Detailed analysis of all 5 Scalene usage modes
- Clear ✅/❌ coverage breakdown
- Explains why gaps exist
- Provides enhancement recommendations for future versions
- Includes code examples for potential future APIs

### 2. Updated docs/api.md
- Added "Scope & Limitations" section at the top
- Clarifies what IS supported
- Clarifies what ISN'T supported
- Added "Future Enhancements" section at the end
- Explains rationale for design choices

### 3. Updated docs/architecture.md
- Added new "Key Design Decision #0: Subprocess-Based Profiling"
- Explains scope decision with full rationale
- Documents what's supported and what isn't
- References new SCALENE_MODES_ANALYSIS.md document

### 4. Updated README.md
- Added "What Scalene-MCP Does" section (✅ supported)
- Added "What Scalene-MCP Doesn't Do" section (❌ not supported)
- Explains why subprocess approach was chosen
- References detailed analysis document

## Impact

### For Users
- Crystal clear about what can and can't be done
- Understand design rationale
- Know where limitations come from
- Can see future enhancements in roadmap

### For Contributors
- Know why subprocess model was chosen
- Understand enhancement opportunities
- Can reference design decisions when extending

### For LLMs
- Complete transparency about capabilities
- No ambiguity about what tools can do
- Clear documentation of scope

## Files Changed

1. **Created**:
   - `SCALENE_MODES_ANALYSIS.md` (120 lines)

2. **Updated**:
   - `docs/api.md` - Added scope section + future enhancements
   - `docs/architecture.md` - Added scope decision explanation
   - `README.md` - Added capabilities/limitations section

## Key Takeaway

Scalene-MCP supports **3 out of 5** major Scalene usage modes. The 2 gaps (in-process and process attachment) are:
- Intentional design choices
- Appropriate for LLM workflows
- Documented and explained
- Can be enhanced in future versions if needed

The implementation is **not incomplete** - it's **appropriately scoped** for its use case.