# MCP Servers - Consolidated Troubleshooting Log

**Repository:** `/Users/aiveo/mcp-servers`
**Last Updated:** 2025-11-04
**Purpose:** Central troubleshooting documentation for all MCP servers in this repository

---

## Table of Contents
1. [General Issues](#general-issues)
2. [MCP-Specific Issues](#mcp-specific-issues)
   - [Asana MCP](#asana-mcp)
   - [Google Calendar MCP](#google-calendar-mcp)
   - [Google Places MCP](#google-places-mcp)
   - [Google Maps MCP](#google-maps-mcp)
   - [Medicare Hospital MCP](#medicare-hospital-mcp)
3. [Common Solutions](#common-solutions)
4. [Best Practices](#best-practices)

---

## General Issues

### Issue: MCP Servers Not Auto-Discovered by Claude Code
**Status:** Resolved - Fundamental Misunderstanding
**Date:** 2025-11-04

#### Problem
MCP servers with `mcp.json` files were not appearing in Claude Code's tool list.

#### Root Cause
**Critical Misunderstanding:** Claude Code does NOT support auto-discovery of MCP servers.

**Reality:**
- MCP servers MUST be manually added using `claude mcp add` CLI command
- The `mcp.json` files in individual server directories serve documentation purposes only
- Configuration is stored in `/Users/aiveo/.claude.json` (user config) or project-specific `.mcp.json`

#### Resolution
Use the manual configuration process:
```bash
claude mcp add --transport stdio <server-name> -- \
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  /Users/aiveo/mcp-servers/<server_directory>/<script_name>.py
```

**Key Learning:** Always verify documentation against official sources. The auto-discovery concept was a misunderstanding.

---

### Issue: Environment Variables Not Loading from .env Files
**Status:** Resolved
**Date:** 2025-11-04
**Affected Servers:** asana_mcp, google_places_mcp

#### Problem
Servers reported missing environment variables (e.g., API tokens, access keys) even though `.env` files existed with valid values.

**Error Examples:**
- `Configuration Error: ASANA_ACCESS_TOKEN environment variable not set`
- `Error: Google Maps API key not configured`

#### Root Cause
Python's `os.getenv()` only reads environment variables from the process environment, NOT from `.env` files automatically. The `python-dotenv` package and `load_dotenv()` call are required but were missing.

#### Resolution

**Step 1:** Add `python-dotenv` to requirements.txt:
```
python-dotenv>=1.0.0
```

**Step 2:** Update server code to load .env file:
```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Now os.getenv() will work correctly
API_KEY = os.getenv("API_KEY_NAME")
```

**Step 3:** Install dependencies and restart:
```bash
cd /Users/aiveo/mcp-servers/<server_directory>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt
# Then restart Claude Code or the MCP server
```

#### Verification
Test that .env loading works:
```bash
cd /Users/aiveo/mcp-servers/<server_directory>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Loaded!' if os.getenv('YOUR_VAR') else 'Failed')"
```

**Key Learning:** `.env` files are NOT automatically loaded by Python. You MUST use `load_dotenv()` BEFORE any `os.getenv()` calls.

---

### Issue: Wrong Python Command in MCP Configuration
**Status:** Resolved
**Date:** 2025-11-04

#### Problem
Servers failed to start with error: `pyenv: python: command not found`

#### Root Cause
Using generic `python` or `python3` commands instead of absolute path to specific Python version.

**Old Configuration (WRONG):**
```json
{
  "command": "python",  // L pyenv doesn't have 'python' alias
  "args": ["/path/to/script.py"]
}
```

**Correct Configuration:**
```json
{
  "command": "/Users/aiveo/.pyenv/versions/3.11.9/bin/python3",  //  Absolute path
  "args": ["/path/to/script.py"]
}
```

#### Resolution
Always use absolute paths to the specific Python version:
```bash
claude mcp add --transport stdio server-name -- \
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  /Users/aiveo/mcp-servers/server_dir/server.py
```

**Key Learning:** Always use absolute path to specific Python version, especially when using pyenv.

---

### Issue: Missing Dependencies on Fresh Installation
**Status:** Resolved
**Date:** 2025-11-04
**Affected Servers:** google_maps_mcp, medicare_hospital_mcp

#### Problem
Server crashed on startup with `ModuleNotFoundError: No module named '<package>'`

#### Root Cause
Dependencies listed in `requirements.txt` were not installed before adding the MCP server to Claude Code.

#### Resolution
Always install dependencies BEFORE adding the MCP server:
```bash
cd /Users/aiveo/mcp-servers/<server_directory>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt
```

Then add the server:
```bash
claude mcp add --transport stdio <server-name> -- \
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  /Users/aiveo/mcp-servers/<server_directory>/server.py
```

#### Verification
```bash
# Verify all required packages are installed
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip list

# Test server can start (should wait for stdin without errors)
cd /Users/aiveo/mcp-servers/<server_directory>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 server.py
# Press Ctrl+C to exit
```

**Key Learning:** Add dependency installation to standard setup checklist.

---

## MCP-Specific Issues

### Asana MCP

#### Issue: Relative vs Absolute Path in args Field
**Status:** Resolved
**Date:** 2025-11-04

**Problem:** Server failed to connect when using absolute path in args field.

**Root Cause:**
- Using absolute path prevented Claude Code from setting correct working directory
- This caused `.env` file to not be found
- Also triggered pyenv errors

**Wrong Configuration:**
```json
{
  "args": ["/Users/aiveo/mcp-servers/asana_mcp/asana_mcp.py"]  // L Absolute path
}
```

**Correct Configuration:**
```json
{
  "args": ["asana_mcp.py"]  //  Relative path
}
```

**Note:** This was specific to the old auto-discovery approach. With manual `claude mcp add`, use absolute paths.

---

#### Issue: Default Workspace GID Feature
**Status:** Feature Implemented
**Date:** 2025-11-04

**Enhancement:** Added support for `ASANA_DEFAULT_WORKSPACE_GID` environment variable.

**Configuration:**
Add to `.env` file:
```bash
ASANA_ACCESS_TOKEN=your_token_here
ASANA_DEFAULT_WORKSPACE_GID=1205656411889912
```

**Benefit:** Eliminates need to provide `workspace_gid` with every tool call.

**How to Get Workspace GID:**
1. Open Asana in browser
2. Navigate to any page in your workspace
3. Look at URL: `https://app.asana.com/0/1205656411889912/home`
4. The number after `/0/` is your workspace GID

---

### Google Calendar MCP

#### Issue: Missing OAuth2 Access Token Configuration
**Status:** Unresolved
**Date:** 2025-11-04

**Problem:**
```
Configuration Error: GOOGLE_CALENDAR_ACCESS_TOKEN environment variable not set.
Please set it with a valid OAuth2 access token.
```

**Details:**
- **Tool Used:** `mcp__google-calendar-mcp__gcal_create_event`
- **Error Type:** Configuration Error
- **Root Cause:** `GOOGLE_CALENDAR_ACCESS_TOKEN` environment variable not configured

**Required Resolution Steps:**
1. Set up OAuth2 authentication for Google Calendar API
2. Obtain a valid OAuth2 access token
3. Add `GOOGLE_CALENDAR_ACCESS_TOKEN` to `.env` file:
   ```bash
   GOOGLE_CALENDAR_ACCESS_TOKEN=your_oauth2_token_here
   ```
4. Ensure `load_dotenv()` is called in the server code
5. Restart the MCP server

**Additional Notes:**
- Google Calendar requires OAuth2 authentication (not just an API key)
- Access tokens may need to be refreshed periodically
- Consider implementing refresh token logic for long-term usage

**References:**
- [Google Calendar API OAuth2 Documentation](https://developers.google.com/calendar/api/guides/auth)

---

### Google Places MCP

#### Issue: MCP Server Not Appearing After Configuration
**Status:** Resolved
**Date:** 2025-11-04

**Problem:** Server not showing up in Claude Code's MCP tool list despite proper configuration.

**Root Cause:** See "General Issues - MCP Servers Not Auto-Discovered" above.

**Resolution:** Used manual configuration via `claude mcp add` command.

---

#### Issue: Missing .env File Loading
**Status:** Resolved
**Date:** 2025-11-04

**Problem:**
```
Error: Google Maps API key not configured.
Please set the GOOGLE_MAPS_API_KEY environment variable.
```

Even though `.env` file existed with valid API key.

**Root Cause:** Server was using `os.getenv()` without calling `load_dotenv()` first.

**Resolution:**

**Before (BROKEN):**
```python
import os
# ... other imports ...

# Get API key from environment
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")  # L Returns empty string
```

**After (WORKING):**
```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()  #  This loads the .env file!

# Get API key from environment
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")  #  Now works correctly!
```

Also updated `requirements.txt` to include:
```
python-dotenv>=1.0.0
```

---

### Google Maps MCP

#### Issue: Missing googlemaps Package
**Status:** Resolved
**Date:** 2025-11-04

**Problem:**
```
ModuleNotFoundError: No module named 'googlemaps'
```

**Root Cause:** The `googlemaps` package was not installed.

**Resolution:**
```bash
cd /Users/aiveo/mcp-servers/google_maps_mcp
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt
```

**Verification:**
```bash
python3 -c "import googlemaps; print('Success')"
```

---

### Medicare Hospital MCP

#### Issue: Missing fastmcp Package
**Status:** Resolved
**Date:** 2025-11-04

**Problem:** Server couldn't start because `fastmcp` package was missing.

**Resolution:**
```bash
cd /Users/aiveo/mcp-servers/medicare_hospital_mcp
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt
```

This installed:
- `fastmcp-2.13.0.2` (primary requirement)
- Additional supporting dependencies

**Note:** Medicare Hospital MCP uses publicly accessible data from data.cms.gov and does NOT require API keys or authentication.

---

## Common Solutions

### Debugging MCP Connection Issues

#### 1. Check Claude Code Logs
```bash
# View latest debug log
cat ~/.claude/debug/latest | grep -A 10 -B 5 "<server-name>"

# Find error patterns
grep -r "<server-name>.*stderr" ~/.claude/debug/ 2>/dev/null | tail -20
```

#### 2. List Current MCP Servers
```bash
claude mcp list
# All servers should show:  Connected
```

#### 3. Check MCP Server Logs
```bash
# Log location for each server:
/Users/aiveo/Library/Caches/claude-cli-nodejs/-Users-aiveo-mcp-servers/mcp-logs-<server-name>/
```

#### 4. Test Server Manually
```bash
cd /Users/aiveo/mcp-servers/<server_directory>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 server.py
# Should wait for stdin without errors (Ctrl+C to exit)
```

#### 5. Verify Dependencies
```bash
cd /Users/aiveo/mcp-servers/<server_directory>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt
```

#### 6. Test .env Loading
```bash
cd /Users/aiveo/mcp-servers/<server_directory>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Token:', os.getenv('YOUR_ENV_VAR'))"
```

---

### Standard MCP Installation Checklist

Before adding a new MCP server to Claude Code:

- [ ] Verify server code exists at intended location
- [ ] Check `requirements.txt` exists
- [ ] **Ensure `python-dotenv` is in `requirements.txt` if using `.env` files**
- [ ] **Verify server imports and calls `load_dotenv()` before reading env vars**
- [ ] Install dependencies:
  ```bash
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt
  ```
- [ ] Test server can import required modules:
  ```bash
  python3 -c "import <module>; print('Success')"
  ```
- [ ] Test server runs without errors:
  ```bash
  python3 server.py  # Should wait for stdin
  ```
- [ ] Verify API keys in `.env` file (if required)
- [ ] **Test .env loading:**
  ```bash
  python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('API_KEY_NAME'))"
  ```
- [ ] Use `claude mcp add --help` to confirm syntax
- [ ] Add server with absolute paths:
  ```bash
  claude mcp add --transport stdio <server-name> -- \
    /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
    /Users/aiveo/mcp-servers/<server_dir>/server.py
  ```
- [ ] Verify connection:
  ```bash
  claude mcp list
  ```
- [ ] If failed, check logs:
  ```bash
  /Users/aiveo/Library/Caches/claude-cli-nodejs/-Users-aiveo-mcp-servers/mcp-logs-<name>/
  ```

---

## Best Practices

### 1. Environment Variable Management
- **Always use `python-dotenv`** for loading `.env` files
- Call `load_dotenv()` at the top of your server code, before any `os.getenv()` calls
- Keep sensitive credentials in `.env` files, never hardcode them
- Add `.env` to `.gitignore` to prevent committing secrets
- Create `.env.example` files with placeholder values for documentation

### 2. Python Path Configuration
- **Use absolute paths** for Python executable: `/Users/aiveo/.pyenv/versions/3.11.9/bin/python3`
- **Use absolute paths** for server scripts when using `claude mcp add`
- Never rely on `python` or `python3` aliases when using pyenv

### 3. Dependency Management
- Always maintain an accurate `requirements.txt` file
- Include `python-dotenv>=1.0.0` if using `.env` files
- Install dependencies BEFORE adding server to Claude Code
- Document any special installation requirements in README.md

### 4. Configuration Standards
- Use kebab-case for server names with `-mcp` suffix (e.g., `google-maps-mcp`)
- Keep server names consistent across CLI, code, and documentation
- Document all required environment variables in README.md and `.env.example`

### 5. Testing and Validation
- Test server startup manually before adding to Claude Code
- Verify all environment variables load correctly
- Check that all dependencies import successfully
- Review Claude Code logs when issues occur

### 6. Documentation
- Maintain up-to-date README.md for each MCP server
- Document troubleshooting steps in this central log
- Include setup instructions and example usage
- Document all configuration requirements

---

## Quick Reference

### Command Templates

**Add MCP Server:**
```bash
claude mcp add --transport stdio <server-name> -- \
  /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  /Users/aiveo/mcp-servers/<server_dir>/<script>.py
```

**Remove MCP Server:**
```bash
claude mcp remove <server-name>
```

**List MCP Servers:**
```bash
claude mcp list
```

**Install Dependencies:**
```bash
cd /Users/aiveo/mcp-servers/<server_dir>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt
```

**Test Server:**
```bash
cd /Users/aiveo/mcp-servers/<server_dir>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 <script>.py
# Ctrl+C to exit
```

---

## Contact & Resources

### Getting Help
- **Claude Code Documentation:** https://docs.claude.com/claude-code
- **MCP Protocol Documentation:** https://modelcontextprotocol.io
- **FastMCP GitHub:** https://github.com/jlowin/fastmcp

### Debug Locations
- **User Config:** `/Users/aiveo/.claude.json`
- **Debug Logs:** `~/.claude/debug/latest`
- **Server Logs:** `/Users/aiveo/Library/Caches/claude-cli-nodejs/-Users-aiveo-mcp-servers/`

---

**Last Updated:** 2025-11-04
**Maintained By:** Repository Owner
**Purpose:** Central troubleshooting resource for all MCP servers
