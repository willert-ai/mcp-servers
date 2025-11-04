# Troubleshooting Log: google_places_mcp Not Appearing in MCP List

**Date:** 2025-11-04
**Issue:** google_places_mcp server not showing up in Claude Code's MCP tool list
**Status:** Pending restart verification

---

## Issue Description

After installation and configuration, the google_places_mcp is not appearing in Claude Code's available MCP tools list. Expected tools with prefix `mcp__google-places-mcp__*` are not visible.

---

## What We've Checked

### ✅ 1. Directory Structure
**Location:** `/Users/aiveo/mcp-servers/google_places_mcp/`
**Status:** EXISTS and properly structured

```bash
drwxr-xr-x  17 aiveo  staff    544 Nov  4 00:54 .
Files present:
- server.py ✅
- mcp.json ✅
- requirements.txt ✅
- .env ✅
- README.md ✅
```

**Result:** ✅ Directory structure is correct

---

### ✅ 2. mcp.json Configuration
**File:** `/Users/aiveo/mcp-servers/google_places_mcp/mcp.json`

```json
{
  "name": "google-places-mcp",
  "description": "Google Places MCP Server for property research using Google Maps Platform APIs",
  "command": "/Users/aiveo/.pyenv/versions/3.11.9/bin/python3",
  "args": ["server.py"],
  "env": {}
}
```

**Validation:**
- ✅ Name follows kebab-case with `-mcp` suffix
- ✅ Description is clear and descriptive
- ✅ Command points to absolute Python path
- ✅ Args correctly references server.py
- ✅ env is empty object (uses .env file)
- ✅ JSON syntax is valid

**Result:** ✅ Configuration is correct per README.md requirements

---

### ✅ 3. Python Environment
**Python Path:** `/Users/aiveo/.pyenv/versions/3.11.9/bin/python3`

```bash
$ /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 --version
Python 3.11.9
```

**Result:** ✅ Python executable exists and is accessible

---

### ✅ 4. Dependencies Installation
**Required packages:**

```bash
$ cd /Users/aiveo/mcp-servers/google_places_mcp && python3 -m pip list | grep -E "(mcp|httpx|pydantic)"
httpx                      0.28.1
httpx-sse                  0.4.3
mcp                        1.20.0
mcp-memory                 0.5.0
mcp-server-time            1.0.4
pydantic                   2.12.3
pydantic-settings          2.7.2
pydantic_core              2.27.2
```

**MCP Import Test:**
```bash
$ python3 -c "import sys; import mcp; print('MCP import successful')"
MCP import successful
```

**Result:** ✅ All dependencies are installed and importable

---

### ✅ 5. API Key Configuration
**File:** `/Users/aiveo/mcp-servers/google_places_mcp/.env`

```bash
$ test -s .env && grep -q "GOOGLE_MAPS_API_KEY=" .env && echo "API key is configured"
API key is configured
```

**Result:** ✅ .env file exists and contains GOOGLE_MAPS_API_KEY

---

### ✅ 6. Server Code Validation
**File:** `/Users/aiveo/mcp-servers/google_places_mcp/server.py`

Key components verified:
- ✅ Imports are correct (mcp, httpx, pydantic)
- ✅ FastMCP initialization: `mcp = FastMCP("google_places_mcp")`
- ✅ API key loading: `API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")`
- ✅ Server structure appears valid

**Result:** ✅ Server code structure is correct

---

### ✅ 7. Comparison with Working MCP Servers

**google_maps_mcp mcp.json:**
```json
{
  "name": "google-maps-mcp",
  "command": "/Users/aiveo/.pyenv/versions/3.11.9/bin/python3",
  "args": ["server.py"],
  "env": {}
}
```

**asana_mcp mcp.json:**
```json
{
  "name": "asana-mcp",
  "command": "/Users/aiveo/.pyenv/versions/3.11.9/bin/python3",
  "args": ["asana_mcp.py"],
  "env": {}
}
```

**Result:** ✅ google_places_mcp configuration matches pattern of other MCPs

---

### ✅ 8. Auto-Discovery Status

**Current MCP Servers Found:**
```bash
$ find /Users/aiveo/mcp-servers -name "mcp.json" -type f
./google_maps_mcp/mcp.json
./medicare_hospital_mcp/mcp.json
./google_calendar_mcp/mcp.json
./google_places_mcp/mcp.json
./asana_mcp/mcp.json
```

**Available MCP Tools in Current Session:**
- `mcp__perplexity__*` (built-in)
- `mcp__ide__*` (built-in)
- ❌ NO custom MCP servers from `/Users/aiveo/mcp-servers/` are loaded

**Result:** ⚠️ Claude Code has NOT loaded ANY of the custom MCP servers

---

## Root Cause Analysis

**Finding:** None of the custom MCP servers from `/Users/aiveo/mcp-servers/` are currently loaded in Claude Code, including:
- google_places_mcp
- google_maps_mcp
- asana_mcp
- google_calendar_mcp
- medicare_hospital_mcp

**Reason:** Claude Code's auto-discovery only runs at startup. The servers have not been loaded into the current Claude Code session.

**Evidence:** Only built-in MCPs (`mcp__perplexity__*`, `mcp__ide__*`) are visible, no custom MCPs with prefix `mcp__<server-name>__*` are available.

---

## Solution

### Required Action: Restart Claude Code

Claude Code needs to be completely restarted to trigger auto-discovery and load all MCP servers.

**Steps:**
1. Exit Claude Code completely (⌘Q or File → Quit)
2. Relaunch Claude Code
3. Wait for initialization to complete
4. Verify MCP tools are loaded

---

## Verification Checklist (After Restart)

After restarting Claude Code, verify the following tools are available:

### google_places_mcp Tools Expected:
- [ ] `mcp__google-places-mcp__google_places_nearby_search`
- [ ] `mcp__google-places-mcp__google_places_search_text`
- [ ] `mcp__google-places-mcp__google_places_get_place_details`
- [ ] `mcp__google-places-mcp__google_places_autocomplete`
- [ ] `mcp__google-places-mcp__routes_compute_routes`
- [ ] `mcp__google-places-mcp__geocode_address`
- [ ] `mcp__google-places-mcp__reverse_geocode`

### Other Expected MCP Tools:
- [ ] `mcp__google-maps-mcp__*` tools
- [ ] `mcp__asana-mcp__*` tools
- [ ] `mcp__google-calendar-mcp__*` tools
- [ ] `mcp__medicare-hospital-mcp__*` tools

---

## If Still Not Working After Restart

If the MCP still doesn't load after restart, check these additional items:

### 1. Claude Code Logs
- Check Claude Code startup logs for errors
- Look for messages about MCP server initialization

### 2. Server Manual Test
```bash
cd /Users/aiveo/mcp-servers/google_places_mcp
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 server.py
# Should start without errors (will wait for stdin)
```

### 3. JSON Validation
```bash
cat /Users/aiveo/mcp-servers/google_places_mcp/mcp.json | python3 -m json.tool
# Should output formatted JSON without errors
```

### 4. File Permissions
```bash
ls -la /Users/aiveo/mcp-servers/google_places_mcp/
# Ensure server.py and mcp.json are readable
```

### 5. Working Directory Test
```bash
cd /Users/aiveo/mcp-servers/google_places_mcp
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -c "import os; print(os.path.exists('server.py'))"
# Should print: True
```

---

## Summary

**Configuration Status:** ✅ ALL CHECKS PASSED
**Installation Status:** ✅ COMPLETE
**Current Status:** ✅ RESOLVED (2025-11-04)
**Resolution Method:** Manual configuration via CLI

---

## ROOT CAUSE ANALYSIS

### Critical Misunderstanding: Auto-Discovery Myth

**Initial Assumption (INCORRECT):**
- Believed Claude Code automatically discovers MCP servers from directories containing `mcp.json` files
- Expected servers to load on restart without manual configuration
- Created elaborate directory structure based on this false assumption

**Reality (CORRECT):**
- **Claude Code does NOT support auto-discovery**
- MCP servers MUST be manually added using `claude mcp add` CLI command
- The `mcp.json` files in individual server directories serve **no purpose** for Claude Code
- Configuration is stored in `/Users/aiveo/.claude.json` (user config) or project-specific `.mcp.json`

**Source of Confusion:**
- Claude Desktop (different product) uses JSON configuration files
- Documentation may have been misinterpreted or outdated README was created
- The `/Users/aiveo/mcp-servers/README.md` incorrectly documented auto-discovery

---

## ACTUAL ISSUES ENCOUNTERED

### Issue #1: Fundamental Configuration Misunderstanding ⚠️

**Problem:**
- Created `mcp.json` files in each server directory expecting auto-discovery
- No servers appeared in Claude Code because they were never actually registered
- Only asana and google-calendar appeared because they were manually configured previously (with old paths)

**Evidence:**
```bash
# Only these servers had log directories (meaning they were actually configured):
/Users/aiveo/Library/Caches/claude-cli-nodejs/-Users-aiveo-mcp-servers/
├── mcp-logs-asana/
├── mcp-logs-google-calendar/
└── mcp-logs-perplexity/

# These servers had NO log directories (never configured):
- google-places-mcp (MISSING)
- google-maps-mcp (MISSING)
- medicare-hospital-mcp (MISSING)
```

**Resolution:**
- Corrected understanding: Claude Code requires manual `claude mcp add` commands
- Updated README.md to remove all auto-discovery references
- Documented proper manual configuration process

---

### Issue #2: Old/Incorrect MCP Configurations ⚠️

**Problem:**
- asana and google-calendar were configured but failing to connect
- Error logs showed: `pyenv: python: command not found`

**Root Causes:**

**A) Wrong Python Command:**
```json
// OLD CONFIGURATION (WRONG):
{
  "asana": {
    "command": "python",  // ❌ pyenv doesn't have 'python' alias
    "args": ["/Users/aiveo/asana_mcp/asana_mcp.py"]
  }
}
```

**B) Old/Outdated Paths:**
```json
// OLD PATHS (WRONG):
"/Users/aiveo/asana_mcp/asana_mcp.py"           // ❌ Old location
"/Users/aiveo/google_calendar_mcp/google_calendar_mcp.py"  // ❌ Old location

// NEW PATHS (CORRECT):
"/Users/aiveo/mcp-servers/asana_mcp/asana_mcp.py"
"/Users/aiveo/mcp-servers/google_calendar_mcp/google_calendar_mcp.py"
```

**Evidence from Logs:**
```json
{
  "error": "Server stderr: pyenv: python: command not found\n\nThe `python' command exists in these Python versions:\n  3.11.9",
  "timestamp": "2025-11-04T00:38:55.752Z"
}
```

**Resolution:**
- Removed old configurations: `claude mcp remove asana` and `claude mcp remove google-calendar`
- Used correct Python path: `/Users/aiveo/.pyenv/versions/3.11.9/bin/python3`
- Updated all paths to new centralized location: `/Users/aiveo/mcp-servers/`

---

### Issue #3: Missing Dependencies (google-maps-mcp) ⚠️

**Problem:**
- After adding google-maps-mcp, it failed to connect
- Server crashed on startup with module import error

**Error Log:**
```json
{
  "error": "Server stderr: Traceback (most recent call last):\n  File \"/Users/aiveo/mcp-servers/google_maps_mcp/server.py\", line 23, in <module>",
  "error": "Server stderr: import googlemaps\nModuleNotFoundError: No module named 'googlemaps'"
}
```

**Root Cause:**
- The `googlemaps` package was not installed in the Python environment
- `requirements.txt` existed but dependencies were never installed

**Resolution:**
```bash
cd /Users/aiveo/mcp-servers/google_maps_mcp
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt
```

**Lesson Learned:**
- Always verify dependencies are installed before adding MCP server to Claude Code
- Add dependency check to standard setup procedure

---

## CORRECT CONFIGURATION PROCESS

### Step 1: Remove Old/Broken Configurations
```bash
# List current servers
claude mcp list

# Remove any broken servers
claude mcp remove asana
claude mcp remove google-calendar
```

### Step 2: Verify Dependencies
```bash
cd /Users/aiveo/mcp-servers/<server_directory>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt
```

### Step 3: Add Server with Correct Syntax
```bash
claude mcp add --transport stdio <server-name> -- \
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  /Users/aiveo/mcp-servers/<server_directory>/<script_name>.py
```

**Key Points:**
- Use `--transport stdio` for Python-based servers
- Use `--` separator before the command
- Use absolute paths for both Python executable and script
- Server name should use kebab-case with `-mcp` suffix

### Step 4: Verify Connection
```bash
claude mcp list
# All servers should show: ✓ Connected
```

---

## FINAL WORKING CONFIGURATION

### All Servers Successfully Added:

```bash
# 1. google-places-mcp
claude mcp add --transport stdio google-places-mcp -- \
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  /Users/aiveo/mcp-servers/google_places_mcp/server.py

# 2. google-maps-mcp
claude mcp add --transport stdio google-maps-mcp -- \
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  /Users/aiveo/mcp-servers/google_maps_mcp/server.py

# 3. asana-mcp
claude mcp add --transport stdio asana-mcp -- \
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  /Users/aiveo/mcp-servers/asana_mcp/asana_mcp.py

# 4. google-calendar-mcp
claude mcp add --transport stdio google-calendar-mcp -- \
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  /Users/aiveo/mcp-servers/google_calendar_mcp/google_calendar_mcp.py

# 5. medicare-hospital-mcp
claude mcp add --transport stdio medicare-hospital-mcp -- \
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  /Users/aiveo/mcp-servers/medicare_hospital_mcp/server.py
```

### Verification Results:
```
✓ perplexity - Connected
✓ google-places-mcp - Connected
✓ google-maps-mcp - Connected
✓ asana-mcp - Connected
✓ google-calendar-mcp - Connected
✓ medicare-hospital-mcp - Connected
```

---

## LESSONS LEARNED

### 1. Documentation Accuracy ⚠️
**Problem:** Created README.md with incorrect auto-discovery information
**Lesson:** Always verify documentation against official sources before creating setup guides
**Action:** Updated `/Users/aiveo/mcp-servers/README.md` to reflect correct manual configuration process

### 2. Configuration Location 📁
**Learned:** Claude Code stores MCP configuration in `/Users/aiveo/.claude.json`
**Impact:** Understanding this helps debug configuration issues
**Note:** Configuration can be at different scopes (local, user, project)

### 3. Python Environment Specificity 🐍
**Problem:** Using generic `python` command failed in pyenv
**Lesson:** Always use absolute path to specific Python version
**Best Practice:** `/Users/aiveo/.pyenv/versions/3.11.9/bin/python3` (not `python3` or `python`)

### 4. Dependency Installation ⚙️
**Problem:** Server code existed but dependencies weren't installed
**Lesson:** Always run `pip install -r requirements.txt` before adding server
**Best Practice:** Add dependency check to standard setup checklist

### 5. Log File Debugging 🔍
**Learned:** Claude Code creates detailed logs at:
`/Users/aiveo/Library/Caches/claude-cli-nodejs/-Users-aiveo-mcp-servers/mcp-logs-<server-name>/`
**Impact:** These logs are invaluable for debugging connection failures
**Best Practice:** Always check logs when server shows "Failed to connect"

### 6. CLI Help Commands 💡
**Learned:** `claude mcp add --help` provides exact syntax and examples
**Lesson:** Always check CLI help before assuming command structure
**Impact:** Saved time by understanding correct `--` separator syntax

---

## PREVENTION CHECKLIST FOR FUTURE MCP INSTALLATIONS

### Before Adding New MCP Server:

- [ ] Verify server code exists at intended location
- [ ] Check `requirements.txt` exists
- [ ] Install dependencies: `/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt`
- [ ] Test server can import: `python3 -c "import <module>; print('Success')"`
- [ ] Test server runs: `python3 server.py` (should wait for stdin without errors)
- [ ] Verify API keys in `.env` file (if required)
- [ ] Use `claude mcp add --help` to confirm syntax
- [ ] Add server with absolute paths
- [ ] Verify connection: `claude mcp list`
- [ ] Check logs if failed: `/Users/aiveo/Library/Caches/claude-cli-nodejs/-Users-aiveo-mcp-servers/mcp-logs-<name>/`

---

## REFERENCE: CORRECT COMMAND SYNTAX

### General Template:
```bash
claude mcp add --transport stdio <server-name> -- \
  <absolute-path-to-python> \
  <absolute-path-to-script>
```

### Real Example:
```bash
claude mcp add --transport stdio my-service-mcp -- \
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  /Users/aiveo/mcp-servers/my_service_mcp/server.py
```

### Key Elements:
- `--transport stdio` - For process-based servers (Python, Node.js)
- `--` - Separator between Claude Code options and the command
- Absolute paths only (no relative paths)
- Server name in kebab-case with `-mcp` suffix

---

## FINAL STATUS

**Date Resolved:** 2025-11-04
**Total Time to Resolution:** ~2 hours (including investigation)
**Primary Blocker:** Incorrect assumption about auto-discovery
**Secondary Issues:** Wrong Python command, old paths, missing dependencies

**All Issues Resolved:**
- ✅ Corrected fundamental understanding of Claude Code MCP configuration
- ✅ Updated all documentation to reflect manual configuration requirement
- ✅ Removed old/broken configurations
- ✅ Added all 5 MCP servers with correct paths and commands
- ✅ Verified all servers connected successfully
- ✅ Documented comprehensive troubleshooting process for future reference

**Next Steps:**
- Monitor server stability over next few sessions
- Create standard setup script for future MCP server additions
- Consider creating `.env.example` files in each server directory
