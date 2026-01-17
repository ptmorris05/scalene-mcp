# Phase 9: Coverage Gap Analysis Quick Reference

## Total Gap: 107 statements (14.38%)

### 🔴 CRITICAL - Must Fix First

#### storage.py - 0% (59 missing) 
**Entire module uncovered**

```python
# tests/test_storage.py (NEW FILE)
class TestProfileStorage:
    test_storage_init()
    test_store_profile()
    test_retrieve_profile()
    test_list_profiles()
    test_profile_limit()
    test_edge_cases()
```

**Line Coverage**: 1-194 (all lines in storage.py)
**Effort**: 2-3 hours (HIGH PRIORITY)

---

### 🟠 HIGH PRIORITY

#### profiler.py - 83.33% (15 missing)

**Missing Lines**:
```
111, 115, 119, 121, 123    # Argument validation branches
135, 141, 143, 145         # Command building conditionals
182-183                    # Process timeout path
197-198                    # Process kill cleanup
208-209                    # Exception handling
```

**Test Coverage Needed**:
```python
# tests/test_profiler.py (ENHANCE)
- Test timeout with asyncio.TimeoutError
- Test process failures
- Test GPU flag combinations
- Test memory options
- Test exclude/profile-only paths
- Test script arguments parsing
```

**Effort**: 2 hours

---

#### analyzer.py - 86.93% (20 missing)

**Missing Lines & Functions**:
```
159, 166-167          # get_cpu_hotspots() - empty profile edge cases
243-244               # get_memory_hotspots() - threshold filtering
264                   # get_bottlenecks() - empty results
285                   # get_memory_leaks() - no leak scenario
295-303               # Leak detection thresholds
321                   # get_function_summary() - function not found
348, 354              # Stack trace absence handling
407-413               # Exception handling, unknown analysis type
```

**Test Coverage Needed**:
```python
# tests/test_analyzer.py (ENHANCE)
- Empty profile fixtures
- Minimal profile fixtures
- Profiles with no hotspots
- Profiles below thresholds
- Memory leak edge cases
- Missing function lookups
- Profiles without stack traces
```

**Effort**: 2 hours

---

### 🟡 MEDIUM PRIORITY

#### comparator.py - 93.75% (6 missing)

**Missing Lines**: 144, 160, 254, 327-339

**Focus**: Edge cases in profile comparison
- Empty vs populated
- Identical profiles
- Zero-difference comparisons

**Effort**: 1 hour

---

#### parser.py - 96.55% (3 missing)

**Missing Lines**: 56-57, 61

**Focus**: JSON parsing errors
- Malformed JSON
- Missing required fields
- Extra unexpected fields

**Effort**: 30 minutes

---

#### server.py - 98.18% (2 missing)

**Missing Lines**: 666, 670

**Focus**: Exception paths in tools
- Likely already high coverage
- Edge case exceptions

**Effort**: 30 minutes

---

#### logging.py - 88.89% (2 missing)

**Missing Lines**: 22, 38

**Focus**: Logger initialization variations
- Different log levels
- Logger configuration paths

**Effort**: 30 minutes

---

## Implementation Order (Recommended)

### Day 1 (6-8 hours)
1. **storage.py** (2-3 hours) - CRITICAL
2. **profiler.py** (2 hours) - HIGH
3. **analyzer.py** (2 hours) - HIGH

### Day 2 (3-4 hours)
4. **comparator.py** (1 hour) - MEDIUM
5. **parser.py** (0.5 hour) - MEDIUM
6. **server.py** (0.5 hour) - MEDIUM
7. **logging.py** (0.5 hour) - MEDIUM
8. Verify all at 100% (0.5-1 hour)

### Day 3 (Rest of QA)
9. Type checking, linting, documentation, release prep

---

## Testing Strategy

### For storage.py (0% → 100%)
Use black-box testing:
- Create ProfileStorage instance
- Call each public method
- Verify state changes
- Test error conditions

### For profiler.py (83.33% → 100%)
Use mocking:
```python
@patch('asyncio.create_subprocess_exec')
def test_timeout(mock_exec):
    # Test timeout path
```

### For analyzer.py (86.93% → 100%)
Use parametrized fixtures:
```python
@pytest.mark.parametrize("profile,expected", [
    (empty_profile, []),
    (minimal_profile, [hotspot]),
])
def test_hotspots(profile, expected):
```

---

## Coverage Verification

### Check Before Starting
```bash
uv run pytest --cov=src/scalene_mcp --cov-report=term-missing
```

### Check Progress
```bash
# After each major test addition
uv run pytest --cov=src/scalene_mcp src/scalene_mcp/profiler.py --cov-report=term-missing
```

### Check Completion
```bash
# Final verification
uv run pytest --cov=src/scalene_mcp --cov-fail-under=100
```

---

## Expected Results After Phase 9

```
src/scalene_mcp/__init__.py          100% (3)
src/scalene_mcp/models.py           100% (128) ✅ Already perfect
src/scalene_mcp/server.py           100% (110) ⬅ +2 lines
src/scalene_mcp/comparator.py       100% (96)  ⬅ +6 lines
src/scalene_mcp/parser.py           100% (87)  ⬅ +3 lines
src/scalene_mcp/profiler.py         100% (90)  ⬅ +15 lines
src/scalene_mcp/analyzer.py         100% (153) ⬅ +20 lines
src/scalene_mcp/logging.py          100% (18)  ⬅ +2 lines
src/scalene_mcp/storage.py          100% (59)  ⬅ +59 lines (NEW!)
src/scalene_mcp/config.py           100% (0)
src/scalene_mcp/recommender.py      100% (0)
src/scalene_mcp/utils.py            100% (0)

TOTAL                               100% (744)  ✅ COMPLETE!
```

---

## Quick Checklist

- [ ] storage.py tests created (59 statements)
- [ ] profiler.py tests enhanced (15 statements)
- [ ] analyzer.py tests enhanced (20 statements)
- [ ] comparator.py tests enhanced (6 statements)
- [ ] parser.py tests enhanced (3 statements)
- [ ] server.py tests enhanced (2 statements)
- [ ] logging.py tests enhanced (2 statements)
- [ ] All tests pass: `uv run pytest -v`
- [ ] Coverage 100%: `uv run pytest --cov --cov-fail-under=100`
- [ ] No type errors: `uv run mypy src/`
- [ ] No lint errors: `uv run ruff check src/`
- [ ] Documentation reviewed
- [ ] Release prepared (v0.1.0)
