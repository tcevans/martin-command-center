# Code Review: Martin's Command Center Dashboard

**Reviewer:** Edward  
**Date:** 2026-03-02  
**Project:** martin-command-center  
**Verdict:** 🔄 REQUEST_CHANGES

---

## Overall Verdict

**REQUEST_CHANGES**

The dashboard implements the core architecture and mostly follows the design, but has **critical issues** that prevent it from functioning correctly:
1. Wrong SESSION_STATE_PATH configuration
2. GitHub API field mismatches causing all GitHub data to fail
3. Missing theme.py file

---

## Issues Found

### Critical Issues

| # | Issue | Location | Description |
|---|-------|----------|-------------|
| 1 | **Wrong SESSION_STATE_PATH** | `src/config.py` | Config points to `~/.openclaw/workspace-coder/SESSION-STATE.md` but design specifies `~/.openclaw/workspace-architect/SESSION-STATE.md`. The correct path exists and has data; the configured path does not. |
| 2 | **GitHub API Field Mismatch** | `src/data/github.py` | Uses incorrect JSON field names that don't match actual `gh` CLI output. PRs: `headRepository` doesn't exist (should use `headRepositoryOwner`). Runs: `headRepository` doesn't exist. Issues: `repository` doesn't exist. **Result: All GitHub data fails to parse.** |
| 3 | **Missing theme.py** | `src/styles/` | Design specifies `src/styles/theme.py` for color/theme definitions, but file doesn't exist. Styles are inlined in app.py instead. |

### Warning Issues

| # | Issue | Location | Description |
|---|-------|----------|-------------|
| 4 | **UI Widgets Not Separated** | `src/ui/widgets/` | Design specifies separate widget files (`agent_panel.py`, `project_panel.py`, etc.) but they don't exist. All UI logic is inlined in `app.py`. Works but violates architecture. |
| 5 | **No composer.py** | `src/ui/composer.py` | Design specifies layout composer but it's inlined in `app.py`. |
| 6 | **OpenClaw CLI Not Found** | `src/data/openclaw.py` | CLI not available in PATH on this machine. Error handling works (returns empty list), but worth noting for deployment. |
| 7 | **No Logging** | All files | Uses `print()` statements instead of proper logging module. Not production-ready. |

### Suggestions

| # | Issue | Description |
|---|-------|-------------|
| 8 | **Add retry logic** | GitHub API failures could benefit from exponential backoff retry. |
| 9 | **Test coverage** | `test_basic.py` only tests data layer, not UI rendering. Add Textual app tests. |
| 10 | **Environment variable config** | Consider supporting env vars for paths (useful for Docker/testing). |

---

## Architecture Adherence

| Component | Status | Notes |
|-----------|--------|-------|
| File Structure | ⚠️ Partial | Missing: `widgets/*.py`, `composer.py`, `styles/theme.py` |
| Data Layer | ✅ Good | Fetcher, clients implemented correctly |
| Models | ✅ Good | All dataclasses with properties |
| Async Patterns | ✅ Good | Uses `asyncio.gather`, `@work` decorator correctly |
| Error Handling | ✅ Good | `return_exceptions=True`, graceful fallbacks |
| Configuration | ❌ Wrong | Wrong path, missing theme |

---

## Test Results

```
✅ App created successfully
✅ Data fetcher created successfully
📊 Data fetch results:
  - Agents: 0 (OpenClaw CLI not in PATH)
  - Projects: 3 (reads from SESSION-STATE.md)
  - GitHub events: 0 (API field mismatch)
  - Blocked items: 0 (empty file on fallback)
```

The app **runs** but GitHub panel is broken and session state reads from wrong location.

---

## Code Quality Score

**5/10**

- Core functionality works but critical integrations fail
- Good async patterns and error handling
- Violates architecture spec (inline vs separate files)
- Missing required files

---

## Required Changes

### 1. Fix SESSION_STATE_PATH (Critical)
```python
# src/config.py - Line 12
SESSION_STATE_PATH: Path = Path(
    "~/.openclaw/workspace-architect/SESSION-STATE.md"  # Was: workspace-coder
).expanduser()
```

### 2. Fix GitHub API Fields (Critical)

Update `src/data/github.py` to use correct `gh` CLI field names:

**PRs** - use `headRepositoryOwner` not `headRepository`:
```python
repo=pr.get("headRepositoryOwner", {}).get("login", "unknown")
# Or: pr.get("headRefName", "unknown")
```

**Runs** - remove `headRepository`:
```python
# Just use the workflow name, not repo
event = GitHubEvent(
    type="run",
    title=run.get("displayTitle") or run.get("name", "Unknown"),
    status=run["status"],
    repo=run.get("headBranch", "unknown"),  # Instead of headRepository
    ...
)
```

**Issues** - use correct field:
```python
repo=issue.get("repositoryNameWithOwner", "unknown")
# Or skip repo for issues
```

### 3. Create theme.py (Critical)

Create `src/styles/theme.py`:
```python
# Theme configuration
THEME = {
    "success": "green",
    "warning": "yellow", 
    "error": "red",
    "muted": "dim",
    "primary": "blue",
    "secondary": "cyan",
}
```

---

## Non-Blocking Suggestions

- Extract UI widgets to separate files per design
- Add proper logging instead of print()
- Add UI integration tests with Textual testing utilities
- Consider adding environment variable overrides for paths

---

## Review Summary

The implementation shows good understanding of async patterns and error handling, but has two critical bugs that break major functionality (GitHub data and wrong config path). Once fixed, the dashboard should work correctly.

**Next Steps:** Fix the 3 critical issues, then re-review.
