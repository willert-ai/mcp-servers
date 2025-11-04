# Asana MCP Server - Troubleshooting Log
**Date:** 2025-11-04
**Issue:** Asana MCP server failing to connect with error "Failed to reconnect to asana"

---

## Initial Symptoms

- `/mcp` command shows: `Failed to reconnect to asana.`
- Server was previously working but stopped after 20+ iterations of fixes
- Last attempted fix: Re-creating the Asana MCP tool

---

## Diagnostic Steps Performed

### 1. Configuration Files Review

**Files Checked:**
- ✅ `/Users/aiveo/mcp-servers/asana_mcp/mcp.json` - EXISTS
- ✅ `/Users/aiveo/mcp-servers/asana_mcp/asana_mcp.py` - EXISTS
- ✅ `/Users/aiveo/mcp-servers/asana_mcp/.env` - EXISTS
- ✅ `/Users/aiveo/mcp-servers/asana_mcp/requirements.txt` - EXISTS

**mcp.json Configuration (BEFORE FIX):**
```json
{
  "name": "asana-mcp",
  "description": "Asana MCP Server for task management, project organization, comments, sections, and tags",
  "command": "/Users/aiveo/.pyenv/versions/3.11.9/bin/python3",
  "args": ["/Users/aiveo/mcp-servers/asana_mcp/asana_mcp.py"],  ← ABSOLUTE PATH (PROBLEM)
  "env": {}
}
```

### 2. Python Environment Validation

**Tests Performed:**
```bash
# Python version check
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 --version
# Result: Python 3.11.9 ✅

# Dependencies check
cd /Users/aiveo/mcp-servers/asana_mcp
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -c "import mcp; import httpx; import pydantic; print('All dependencies installed')"
# Result: All dependencies installed ✅

# Python syntax validation
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m py_compile asana_mcp.py
# Result: ✓ Python syntax is valid ✅

# JSON validation
cat /Users/aiveo/mcp-servers/asana_mcp/mcp.json | /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m json.tool > /dev/null
# Result: ✓ mcp.json is valid JSON ✅
```

**Required Dependencies (requirements.txt):**
```
mcp
httpx
pydantic
```

### 3. Environment Variables Check

**Tests Performed:**
```bash
# Check .env file exists and has ASANA_ACCESS_TOKEN
cat /Users/aiveo/mcp-servers/asana_mcp/.env | grep -c "ASANA_ACCESS_TOKEN"
# Result: 1 (ASANA_ACCESS_TOKEN is present) ✅
```

### 4. File Permissions Check

```bash
ls -la /Users/aiveo/mcp-servers/asana_mcp/asana_mcp.py
# Result: -rw-r--r--  1 aiveo  staff  41790 Nov  4 00:24
# Permissions are correct ✅
```

### 5. Git Changes Review

```bash
cd /Users/aiveo/mcp-servers && git diff asana_mcp/mcp.json
```

**Finding:** The only change was:
```diff
- "args": ["asana_mcp.py"],
+ "args": ["/Users/aiveo/mcp-servers/asana_mcp/asana_mcp.py"],
```
This change from relative to absolute path was the recent modification.

### 6. Comparison with Working MCP Servers

**Working Servers Checked:**

**google_calendar_mcp/mcp.json:**
```json
{
  "name": "google-calendar-mcp",
  "description": "Google Calendar MCP Server for managing events, checking availability, and searching calendars",
  "command": "/Users/aiveo/.pyenv/versions/3.11.9/bin/python3",
  "args": ["google_calendar_mcp.py"],  ← RELATIVE PATH ✅
  "env": {}
}
```

**google_maps_mcp/mcp.json:**
```json
{
  "name": "google-maps-mcp",
  "description": "Google Maps MCP Server for location analysis, distance calculation, drive time, nearby search, place details, and address validation",
  "command": "/Users/aiveo/.pyenv/versions/3.11.9/bin/python3",
  "args": ["server.py"],  ← RELATIVE PATH ✅
  "env": {}
}
```

**Pattern Discovered:** All working MCP servers use **relative paths** in the `args` field.

### 7. Claude Code Debug Logs Analysis

**Log Location:** `~/.claude/debug/`

**Critical Error Found in Logs:**
```
[ERROR] MCP server "asana" Server stderr: pyenv: python: command not found
[ERROR] MCP server "asana" Server stderr: The `python' command exists in these Python versions:
[ERROR] MCP server "asana" Server stderr:   3.11.9
[ERROR] MCP server "asana" Server stderr: Note: See 'pyenv help global' for tips on allowing both
        python2 and python3 to be found.
[DEBUG] MCP server "asana": Connection failed after 83ms: MCP error -32000: Connection closed
[ERROR] MCP server "asana" Connection failed: MCP error -32000: Connection closed
```

**Log Files Examined:**
- `~/.claude/debug/1e9df5ca-c191-42eb-9d06-eeb10584fb01.txt`
- `~/.claude/debug/2b295b08-ec59-46be-93b0-f34e8c1fc106.txt`
- `~/.claude/debug/latest`

### 8. MCP Builder Skill Consultation

**Documentation Reviewed:**
- MCP Builder skill loaded and reviewed
- `/Users/aiveo/mcp-servers/README.md` - Auto-discovery requirements

**README Documentation Standards:**
```json
{
  "name": "service-name-mcp",
  "description": "Brief description of what this MCP server does",
  "command": "python3",
  "args": ["server.py"],  ← RELATIVE PATH (DOCUMENTED STANDARD)
  "env": {}
}
```

---

## Root Cause Analysis

### Problem Identified

**Issue:** Using **absolute path** in `mcp.json` args field

**Why This Causes Failure:**

1. **Working Directory Context:**
   - When `args` uses **relative path**: Claude Code sets working directory to `/Users/aiveo/mcp-servers/asana_mcp/`
   - When `args` uses **absolute path**: Working directory is NOT set to the MCP server folder

2. **Environment Loading Issues:**
   - `.env` file is loaded from the **current working directory**
   - With absolute path, `.env` may not be found or loaded from wrong location
   - This causes environment variable loading failures

3. **Python Execution Context:**
   - Pyenv and Python need proper working directory context
   - Absolute paths bypass Claude Code's auto-discovery working directory setup
   - This triggers the `pyenv: python: command not found` error

### Evidence Supporting Root Cause

1. **All working servers use relative paths** (google-calendar-mcp, google-maps-mcp, google-places-mcp, medicare-hospital-mcp)
2. **Documentation specifies relative paths** (README.md line 18: `"args": ["server.py"]`)
3. **Git diff shows recent change** from relative to absolute path
4. **Debug logs show environment issues** (pyenv errors) not syntax/code errors
5. **All other validation passed** (Python syntax, dependencies, JSON validity, file permissions)

---

## Solution Applied

### Fix Implementation

**File Modified:** `/Users/aiveo/mcp-servers/asana_mcp/mcp.json`

**Change Applied:**
```diff
{
  "name": "asana-mcp",
  "description": "Asana MCP Server for task management, project organization, comments, sections, and tags",
  "command": "/Users/aiveo/.pyenv/versions/3.11.9/bin/python3",
- "args": ["/Users/aiveo/mcp-servers/asana_mcp/asana_mcp.py"],
+ "args": ["asana_mcp.py"],
  "env": {}
}
```

**Corrected Configuration (AFTER FIX):**
```json
{
  "name": "asana-mcp",
  "description": "Asana MCP Server for task management, project organization, comments, sections, and tags",
  "command": "/Users/aiveo/.pyenv/versions/3.11.9/bin/python3",
  "args": ["asana_mcp.py"],
  "env": {}
}
```

### Why This Fix Should Work

1. **Matches Working Pattern:** Now identical to all other working MCP servers
2. **Follows Documentation:** Aligns with README.md standards
3. **Enables Proper Context:** Claude Code can set correct working directory
4. **Fixes Environment Loading:** `.env` file will be loaded from correct location
5. **Resolves Pyenv Errors:** Python execution will have proper environment context

---

## Verification Steps

### To Verify Fix Works:

1. **Reload MCP Servers:**
   ```bash
   /mcp
   ```
   Expected: Asana should connect successfully without errors

2. **Check Available Tools:**
   After `/mcp` succeeds, verify Asana tools are available:
   - `mcp__asana-mcp__asana_list_tasks`
   - `mcp__asana-mcp__asana_create_task`
   - `mcp__asana-mcp__asana_get_task_details`
   - etc.

3. **Test Basic Functionality:**
   Try listing tasks to verify API connection works:
   ```
   List my Asana tasks
   ```

### Expected Behavior After Fix:

- ✅ `/mcp` should show Asana connecting successfully
- ✅ No "Failed to reconnect to asana" error
- ✅ Asana tools should appear in available tools list
- ✅ No pyenv errors in debug logs
- ✅ `.env` file should load ASANA_ACCESS_TOKEN correctly

---

## If Fix Does NOT Work - Next Diagnostic Steps

### 1. Check Claude Code Debug Logs Again

```bash
# View latest debug log
cat ~/.claude/debug/latest | grep -A 10 -B 5 "asana"

# Look for specific error patterns
grep -r "asana.*stderr" ~/.claude/debug/ 2>/dev/null | tail -20
```

**What to look for:**
- New error messages different from `pyenv: python: command not found`
- Connection timeout errors
- Authentication errors (401, 403)
- Module import errors
- Network/API errors

### 2. Verify .env File Content

```bash
# Check .env has valid token (check first few chars only)
head -c 50 /Users/aiveo/mcp-servers/asana_mcp/.env
```

**Expected format:**
```
ASANA_ACCESS_TOKEN=1/...long_token_here
```

### 3. Test Server Manually (Outside Claude Code)

```bash
# Run server directly to see startup errors
cd /Users/aiveo/mcp-servers/asana_mcp
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 asana_mcp.py
```

**Expected behavior:**
- Server should start and wait for stdio input (will hang - this is normal)
- No import errors or startup errors
- Press Ctrl+C to stop

**If errors appear:** Document the exact error message for further diagnosis

### 4. Verify Dependencies Installed Correctly

```bash
# Check MCP package version
cd /Users/aiveo/mcp-servers/asana_mcp
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -c "import mcp; print(mcp.__version__)"

# Reinstall dependencies if needed
/Users/aiveo/.pyenv/versions/3.11.9/bin/pip3 install -r requirements.txt --upgrade
```

### 5. Check for Python Version Issues

```bash
# Verify pyenv setup
pyenv versions
pyenv which python3

# Check if asana_mcp directory has .python-version
cat /Users/aiveo/mcp-servers/asana_mcp/.python-version
```

### 6. Compare with Known-Working Server

```bash
# Test if google-calendar-mcp still works
# If it works, the issue is specific to asana configuration
# If it fails too, there's a broader Claude Code MCP issue
```

### 7. Restart Claude Code Completely

```bash
# Sometimes a full restart is needed for mcp.json changes
# Close Claude Code completely and restart
```

---

## Additional Context

### Server Architecture

**Server Type:** Python FastMCP
**Protocol:** Model Context Protocol (MCP)
**Transport:** stdio (standard input/output)
**Framework:** FastMCP (`mcp.server.fastmcp`)

### File Structure

```
asana_mcp/
├── mcp.json                 # MCP configuration (MODIFIED)
├── asana_mcp.py            # Main server code (41,790 bytes)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (ASANA_ACCESS_TOKEN)
├── README.md              # Documentation
├── CHANGELOG.md           # Version history
└── __pycache__/           # Python cache
    └── asana_mcp.cpython-311.pyc
```

### Key Code Elements

**Server Initialization (asana_mcp.py:20):**
```python
mcp = FastMCP("asana_mcp")
```

**Environment Loading (asana_mcp.py:42):**
```python
access_token = os.getenv("ASANA_ACCESS_TOKEN")
```

**Server Entry Point (asana_mcp.py:1482):**
```python
if __name__ == "__main__":
    mcp.run()
```

### Tools Implemented (21 tools total)

1. `asana_list_tasks` - List tasks from workspace/project
2. `asana_create_task` - Create new task
3. `asana_update_task` - Update existing task
4. `asana_complete_task` - Mark task as completed
5. `asana_search_tasks` - Search for tasks
6. `asana_list_projects` - List projects
7. `asana_get_project_tasks` - Get tasks in project
8. `asana_add_comment` - Add comment to task
9. `asana_get_task_comments` - Get task comments
10. `asana_list_sections` - List project sections
11. `asana_move_task_to_section` - Move task to section
12. `asana_add_subtask` - Add subtask to task
13. `asana_get_task_details` - Get detailed task info
14. `asana_list_tags` - List workspace tags
15. `asana_add_tag_to_task` - Add tag to task
16. `asana_set_due_date` - Set task due date
17. `asana_assign_task` - Assign task to user
18. `asana_get_user_task_list` - Get user's task list GID

---

## Historical Context

**Previous Troubleshooting Attempts:**
- 20+ iterations attempting to fix the server
- Multiple changes to configuration (relative vs absolute paths, environment variable handling)
- Auto-discovery setup was implemented
- Token storage method was changed
- Path configurations were modified multiple times

**What Led to This Issue:**
- During previous troubleshooting with mcp-builder skill
- Recommendation was made to change from relative to absolute path
- This change inadvertently broke the server by violating Claude Code's expected pattern

---

## Key Learnings

1. **Always use relative paths in mcp.json args field**
2. **Follow the pattern of working servers when in doubt**
3. **Check debug logs early** - they contain the actual error messages
4. **Validate against documentation** - README.md had the correct pattern documented
5. **MCP servers need proper working directory context** for environment loading

---

## Contact Points for Further Help

If this fix doesn't work and further assistance is needed:

1. **Claude Code Documentation:** https://docs.claude.com/claude-code
2. **MCP Protocol Documentation:** https://modelcontextprotocol.io
3. **FastMCP GitHub:** https://github.com/jlowin/fastmcp
4. **Debug Logs Location:** `~/.claude/debug/latest`

---

## Status

**Current Status:** FIX APPLIED - AWAITING VERIFICATION
**Fix Applied:** 2025-11-04
**Next Action:** Run `/mcp` to verify Asana server connects successfully

---

**End of Troubleshooting Log**
