# Bug Fix: UUID Dependencies Without Mapping

## Issue Description

IntentGraph was outputting UUID dependencies without providing a mapping from UUID to file path, making the dependencies completely unusable.

### Example of Broken Output (Before Fix)

```json
{
  "files": [
    {
      "path": "src/index.ts",
      "dependencies": [
        "0513d3eb-bf45-43a3-a993-415f98702743",
        "6138f687-7dda-4465-99b9-4e9f02a4eb22"
      ]
    }
  ]
}
```

**Problem**: No way to know which files these UUIDs refer to!

## Root Cause

In `src/intentgraph/cli.py`, the `filter_result_by_level()` function was:
1. Converting `FileInfo` objects to dictionaries
2. Stringifying UUID dependencies with `[str(dep) for dep in file_info.dependencies]`
3. **BUT** never including a UUID-to-path mapping in the output

The `FileInfo` model stores dependencies as `list[UUID]` where each UUID references another file's `id` field, but this mapping was lost during filtering.

## The Fix

**File**: `src/intentgraph/cli.py`
**Function**: `filter_result_by_level()`
**Line**: ~67

### Changes Made

```python
def filter_result_by_level(result: AnalysisResult, level: str) -> dict:
    """Filter analysis result based on detail level for AI-friendly output."""

    if level == "full":
        return result.model_dump()

    # ✨ NEW: Build UUID to path mapping for dependencies
    file_id_map = {str(file_info.id): str(file_info.path) for file_info in result.files}

    # Start with basic structure
    filtered_result = {
        "analyzed_at": result.analyzed_at,
        "root": str(result.root),
        "language_summary": {str(k): v.model_dump() for k, v in result.language_summary.items()},
        "file_id_map": file_id_map,  # ✨ NEW: Add UUID to path mapping
        "files": []
    }
    # ... rest of function
```

### Result After Fix

```json
{
  "file_id_map": {
    "0513d3eb-bf45-43a3-a993-415f98702743": "src/core/decision-loop.ts",
    "6138f687-7dda-4465-99b9-4e9f02a4eb22": "src/api/observer-api.ts"
  },
  "files": [
    {
      "path": "src/index.ts",
      "dependencies": [
        "0513d3eb-bf45-43a3-a993-415f98702743",
        "6138f687-7dda-4465-99b9-4e9f02a4eb22"
      ]
    }
  ]
}
```

**Now dependencies can be resolved!**

```python
# Resolve a dependency
dep_uuid = "0513d3eb-bf45-43a3-a993-415f98702743"
resolved_path = data["file_id_map"][dep_uuid]
# => "src/core/decision-loop.ts"
```

## Verification

### Test Case

```bash
cd /mnt/c/Users/nliga/OneDrive/Documents/Repos
export PYTHONPATH="/mnt/c/Users/nliga/OneDrive/Documents/Repos/intentgraph/src:$PYTHONPATH"

python3 -c "
from intentgraph.cli import main
import sys
sys.argv = ['intentgraph', 'PlanB', '--level', 'minimal', '--output', 'test-output.json']
main()
"

# Verify file_id_map exists
python3 -c "
import json
data = json.load(open('test-output.json'))
assert 'file_id_map' in data, 'file_id_map missing!'
assert len(data['file_id_map']) > 0, 'file_id_map empty!'

# Test dependency resolution
for f in data['files']:
    for dep_uuid in f.get('dependencies', []):
        resolved = data['file_id_map'][dep_uuid]
        print(f'{dep_uuid[:20]}... -> {resolved}')
        break
    if f.get('dependencies'):
        break
"
```

### Expected Output

```
fe95c100-ed1a-4cff-a... -> packages/oracle-cmc/src/cmc-client-basic.ts
```

## Impact

### Before Fix
- ❌ Dependencies were UUIDs with no mapping
- ❌ Impossible to determine file relationships
- ❌ AI agents couldn't understand code dependencies
- ❌ Output was essentially broken for dependency analysis

### After Fix
- ✅ `file_id_map` provides UUID-to-path lookup
- ✅ Dependencies can be fully resolved
- ✅ AI agents can trace code relationships
- ✅ Output is actually usable

## Additional Changes

### Script Updates

Updated `multirepo_monitor.sh` to:
1. Use local intentgraph version with PYTHONPATH
2. Changed from `--level minimal` to `--level medium`
3. Medium level includes symbols and exports (requested by user)

### Output Structure (Medium Level)

```json
{
  "analyzed_at": "2026-02-17T07:50:00Z",
  "root": "/path/to/repo",
  "language_summary": { ... },
  "file_id_map": {
    "uuid": "path",
    ...
  },
  "files": [
    {
      "path": "src/file.ts",
      "language": "typescript",
      "dependencies": ["uuid1", "uuid2"],
      "imports": ["import ... from 'module'"],
      "loc": 100,
      "complexity_score": 5,
      "maintainability_index": 0.8,
      "symbols": [
        {
          "name": "functionName",
          "symbol_type": "function",
          "line_start": 10,
          "is_exported": true
        }
      ],
      "exports": [
        {
          "name": "exportName",
          "export_type": "function"
        }
      ],
      "file_purpose": "functional_logic"
    }
  ]
}
```

## Files Modified

1. **src/intentgraph/cli.py** (line ~67)
   - Added `file_id_map` generation
   - Added `file_id_map` to filtered output

2. **multirepo_monitor.sh**
   - Uses PYTHONPATH to load local intentgraph
   - Changed to medium level for symbols/exports

## Testing

All 9 repositories analyzed successfully:
- Verifier (15 files)
- claude-agent-orchestrator (154 files)
- grindbot (150 files)
- grindbot-observatory (39 files)
- grindbot-plugin-contract (5 files)
- grindsim (10 files)
- multirepo-status-sentinel (11 files)
- PlanB (38 files)
- GrindSim_Forge (0 files - empty repo)

**Total output**: 724KB (9 repos)
**Largest**: 316KB (grindbot)

## Recommendation

This fix should be:
1. Committed to the intentgraph repository
2. Added to tests (verify `file_id_map` exists and is correct)
3. Documented in the IntentGraph README/CHANGELOG
4. Released in the next version

---

**Fixed by**: Claude Sonnet 4.5 (AI Assistant)
**Date**: 2026-02-17
**Reported by**: User (nliga)
**Severity**: Critical - core functionality was broken
**Status**: ✅ Fixed and verified
