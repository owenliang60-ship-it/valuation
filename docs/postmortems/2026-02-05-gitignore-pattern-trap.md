# Postmortem: .gitignore Pattern Matching Trap

**Date Discovered**: 2026-02-05
**Severity**: Medium
**System Impact**: Source code tracking
**Status**: Resolved

---

## Symptom

Unable to add source code files in `src/data/` directory to git. `git add` reports files as ignored.

**Observable Behavior**:
```bash
$ git add src/data/data_query.py
The following paths are ignored by one of your .gitignore files:
src/data/data_query.py
Use -f if you really want to add them.

$ git status
# Untracked files not shown (ignored by .gitignore)
```

**User Confusion**: "Why is my source code ignored? I only wanted to ignore the data directory!"

---

## Root Cause

`.gitignore` pattern `data/` (without leading `/`) matches **any** directory named `data` at **any** level in the repository tree.

**Our Directory Structure**:
```
Finance/
├── data/              # Want to ignore (contains large CSV/SQLite files)
│   ├── price/
│   ├── fundamental/
│   └── valuation.db
├── src/
│   └── data/          # Want to track (contains Python modules)
│       ├── __init__.py
│       ├── data_query.py
│       └── fmp_client.py
```

**.gitignore Pattern**:
```gitignore
data/     # Matches BOTH /data/ AND /src/data/
```

**Git Pattern Matching Rules**:
- `data/` → Matches `data/` at any depth
- `/data/` → Matches `data/` only at repository root
- `**/data/` → Explicit "match at any depth" (same as `data/` without `/`)

---

## Impact Timeline

**2026-02-05 10:00** - Attempted to commit new Data Desk modules
**2026-02-05 10:05** - Discovered `src/data/*.py` files ignored by git
**2026-02-05 10:15** - Identified `.gitignore` pattern as root cause
**2026-02-05 10:20** - Changed `data/` → `/data/`, verified fix
**2026-02-05 10:30** - Successfully committed Data Desk source code

---

## Solution

### Immediate Fix
Changed `.gitignore` pattern from `data/` to `/data/`:

```diff
# .gitignore
- data/
+ /data/
```

**Result**:
- `/data/` (root-level data directory) → **ignored**
- `src/data/` (source code directory) → **tracked**

### Verification
```bash
$ git check-ignore -v src/data/data_query.py
# No output = not ignored

$ git check-ignore -v data/price/AAPL.csv
.gitignore:10:/data/    data/price/AAPL.csv
# Correctly ignored
```

---

## Prevention

### Rules
1. **Use `/` prefix for root-level patterns**
   - `/data/` = only root-level `data/` directory
   - `/logs/` = only root-level `logs/` directory

2. **Test .gitignore patterns before committing**
   ```bash
   git check-ignore -v path/to/file
   # Shows which .gitignore rule matched
   ```

3. **Document intent in .gitignore comments**
   ```gitignore
   # Large data files (root level only, not src/data/)
   /data/

   # Log files (any depth)
   *.log
   ```

### Common .gitignore Pitfalls
| Pattern | Matches | Intended? |
|---------|---------|-----------|
| `node_modules/` | Any `node_modules/` at any depth | ✅ Usually yes |
| `build/` | Any `build/` at any depth | ⚠️ Might conflict with `src/build/` |
| `/dist/` | Only root `dist/` | ✅ Explicit |
| `*.pyc` | All `.pyc` files anywhere | ✅ Correct for cache files |

---

## Checklist for .gitignore Patterns

When adding a new ignore pattern:
- [ ] Does the directory name appear elsewhere in the codebase?
- [ ] Should this pattern match at any depth or only root level?
- [ ] Use `/prefix` for root-level patterns
- [ ] Test with `git check-ignore -v <path>`
- [ ] Add comment explaining intent

---

## Related Issues

- **None**: This is a one-time configuration error, now documented for future reference

---

## Lessons Learned

1. **Git Pattern Matching Is Not Intuitive**
   - `data/` without `/` prefix is **not** a root-level pattern
   - Always use `/data/` for root-level directories

2. **Test Before Assuming**
   - `git check-ignore -v` is the definitive test
   - Don't guess based on "what makes sense"

3. **Directory Naming Conflicts Are Common**
   - `data/`, `build/`, `dist/`, `tmp/` often appear multiple times
   - Always be explicit about scope

4. **Document Your .gitignore**
   - Future contributors (including yourself) will forget the rationale
   - Comments prevent accidental pattern changes

---

## References

- Git .gitignore Patterns: https://git-scm.com/docs/gitignore
- `git check-ignore` Manual: https://git-scm.com/docs/git-check-ignore
- GitHub .gitignore Templates: https://github.com/github/gitignore

---

**Author**: Claude (documentation-specialist)
**Reviewed**: 2026-02-08
**Next Review**: When adding new ignore patterns
