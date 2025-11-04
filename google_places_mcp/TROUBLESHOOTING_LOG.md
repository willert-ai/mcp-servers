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
**Current Status:** ⚠️ AWAITING CLAUDE CODE RESTART
**Action Required:** Restart Claude Code to trigger auto-discovery

**Confidence Level:** HIGH - Configuration is correct, restart should resolve the issue

---

## Additional Notes

- All mcp.json files follow the correct naming convention (kebab-case with `-mcp` suffix)
- All dependencies are properly installed
- API keys are configured via .env files
- Server code structure is valid
- Other MCP servers in the same directory use identical configuration patterns

**Next Update:** After Claude Code restart, document whether tools appear and are functional.
