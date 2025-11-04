# MCP Servers Directory

This directory contains Model Context Protocol (MCP) servers for Claude Code.

## Manual Configuration Requirement

**IMPORTANT**: Claude Code does **NOT** use auto-discovery. MCP servers must be manually added using the `claude mcp add` CLI command or by configuring them in Claude Code's settings.

### MCP Server Structure

Each MCP server in this directory should follow this structure for organization and documentation purposes (though Claude Code requires manual configuration via CLI):

**Directory Structure:**
```
mcp-servers/
├── service_name_mcp/          ← Directory uses underscores + _mcp suffix
│   ├── server.py              ← Your server implementation
│   ├── requirements.txt       ← Python dependencies
│   ├── .env                   ← API keys/secrets (gitignored)
│   └── README.md              ← Server documentation
```

**Required for Claude Code:**
- Absolute path to Python executable (e.g., `/Users/aiveo/.pyenv/versions/3.11.9/bin/python3`)
- Absolute path to server file (e.g., `/Users/aiveo/mcp-servers/service_name_mcp/server.py`)
- Environment variables configured via `.env` file in server directory

## Adding MCP Servers to Claude Code

### Method 1: Using CLI (Recommended)

Add servers using the `claude mcp add` command with absolute paths:

```bash
# Add a Python-based MCP server
claude mcp add my-service-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/my_service_mcp/server.py

# Verify it was added
claude mcp list
```

### Method 2: Batch Configuration

To configure all servers in this directory at once, use this helper script:

```bash
cd /Users/aiveo/mcp-servers

# Remove old/broken configurations first
claude mcp remove asana 2>/dev/null || true
claude mcp remove google-calendar 2>/dev/null || true

# Add all servers with correct paths
claude mcp add google-places-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/google_places_mcp/server.py

claude mcp add google-maps-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/google_maps_mcp/server.py

claude mcp add asana-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/asana_mcp/asana_mcp.py

claude mcp add google-calendar-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/google_calendar_mcp/google_calendar_mcp.py

claude mcp add medicare-hospital-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/medicare_hospital_mcp/server.py

# Verify all servers
claude mcp list
```

### Creating a New MCP Server

1. **Create server directory** in `/Users/aiveo/mcp-servers/`
2. **Implement your server** in Python using FastMCP
3. **Create .env file** for API keys (if needed)
4. **Add to Claude Code** using `claude mcp add`
5. **Verify** with `claude mcp list`

**Example:**
```bash
# 1. Create directory
mkdir -p /Users/aiveo/mcp-servers/my_service_mcp
cd /Users/aiveo/mcp-servers/my_service_mcp

# 2. Create server.py
cat > server.py << 'EOF'
from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("my_service_mcp")

@mcp.tool()
def my_tool(query: str) -> str:
    """My tool description"""
    return f"Result for: {query}"

if __name__ == "__main__":
    mcp.run()
EOF

# 3. Create requirements.txt
cat > requirements.txt << 'EOF'
fastmcp
httpx
pydantic
pydantic-settings
EOF

# 4. Install dependencies
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt

# 5. Add to Claude Code
claude mcp add my-service-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/my_service_mcp/server.py
```

## Environment Variables & Security

### 🔒 Recommended Approach: Using `.env` Files

**All MCP servers with API keys or tokens MUST use `.env` files for security.**

Claude Code automatically loads `.env` files from each MCP server directory, making them available to the server process via `os.getenv()`.

#### How to Set Up:

1. **Create a `.env` file** in your MCP server directory:

```bash
# Example: asana_mcp/.env
ASANA_ACCESS_TOKEN=your_token_here
```

```bash
# Example: google_maps_mcp/.env
GOOGLE_MAPS_API_KEY=your_api_key_here
```

2. **Keep `env: {}` empty in `mcp.json`**:

```json
{
  "name": "asana-mcp",
  "description": "Asana task management",
  "command": "python3",
  "args": ["asana_mcp.py"],
  "env": {}
}
```

3. **Load variables in your server code**:

```python
import os
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
```

4. **Ensure `.env` is in `.gitignore`**:

```bash
# .gitignore
.env
```

### ⚠️ Security Best Practices

✅ **DO:**
- Store API keys/tokens in `.env` files
- Add `.env` to `.gitignore`
- Use `env: {}` in `mcp.json`
- Keep secrets out of version control

❌ **DON'T:**
- Hardcode API keys in `mcp.json`
- Commit `.env` files to git
- Share API keys in documentation
- Use the `env` field in `mcp.json` for secrets

### Why This Approach?

- **Automatic Loading**: Claude Code loads `.env` files automatically
- **No Code Changes**: Your server code uses standard `os.getenv()`
- **Security**: Secrets never appear in configuration files
- **Git-Safe**: `.env` files are excluded from version control

## 🎯 Naming Conventions

### Two-Part Naming System

MCP servers use **different naming conventions** for directories vs. configuration:

#### 1. Directory Names (File System)
**Pattern:** `{service}_mcp` with **underscores**

**Rules:**
- Use **underscores** (`_`) to separate words
- Always end with `_mcp` suffix
- Use lowercase only
- Be descriptive but concise

**Examples:**
- ✅ `asana_mcp/`
- ✅ `google_calendar_mcp/`
- ✅ `google_maps_mcp/`
- ❌ `google-calendar-mcp/` (hyphens - wrong)
- ❌ `GoogleCalendarMCP/` (capitals - wrong)
- ❌ `asana/` (missing _mcp - wrong)

#### 2. MCP Server Names (mcp.json)
**Pattern:** `{service}-mcp` with **hyphens** (kebab-case)

**Rules:**
- Use **hyphens** (`-`) to separate words
- Always end with `-mcp` suffix
- Use lowercase only
- Must match the service in directory name

**Examples:**
- ✅ `"name": "asana-mcp"`
- ✅ `"name": "google-calendar-mcp"`
- ✅ `"name": "google-maps-mcp"`
- ❌ `"name": "asana_mcp"` (underscores - wrong)
- ❌ `"name": "google-calendar"` (missing -mcp - wrong)

#### Complete Example

```
Directory Name:        asana_mcp/
├── mcp.json name:    "asana-mcp"         ← Used by Claude Code
├── Python code:      FastMCP("asana_mcp")  ← Internal identifier
├── Tool names:       mcp__asana-mcp__list_tasks
```

**Key Takeaway:**
- **Directories** = `underscores_with_mcp`
- **mcp.json names** = `hyphens-with-mcp`
- **Tool prefixes** = Use the mcp.json name

## 📋 Installed MCP Servers

Current MCP servers in this directory:

| MCP Directory | Purpose | Status | mcp.json |
|---------------|---------|--------|----------|
| `google_calendar_mcp` | Google Calendar event management | ✅ Active | ✅ |
| `asana_mcp` | Asana task management and projects | ✅ Active | ✅ |
| `google_places_mcp` | Property research with Google Maps Platform | ✅ Active | ✅ |
| `google_maps_mcp` | Location analysis, distance calculations | ✅ Active | ✅ |
| `medicare_hospital_mcp` | Hospital quality ratings from Medicare.gov | ✅ Active | ✅ |

### Quick Reference

1. **asana_mcp** - Asana task management and project organization
2. **google_calendar_mcp** - Google Calendar event management
3. **google_maps_mcp** - Location analysis, distance, and drive time calculations
4. **google_places_mcp** - Property research with Google Maps Platform APIs
5. **medicare_hospital_mcp** - Hospital quality ratings from Medicare.gov

## Troubleshooting

### Server not appearing in `claude mcp list`

1. **Add the server manually** using `claude mcp add` (Claude Code does NOT use auto-discovery)
2. **Check absolute paths** - both Python executable and server file must use absolute paths
3. **Verify Python path** - use `/Users/aiveo/.pyenv/versions/3.11.9/bin/python3` (not just `python` or `python3`)
4. **Run `claude mcp list`** to verify configuration

### Server appears but shows "Failed to connect"

1. **Check Python executable path** - ensure it's the correct absolute path
2. **Verify server file path** - ensure absolute path to server.py is correct
3. **Check server logs** in `/Users/aiveo/Library/Caches/claude-cli-nodejs/-Users-aiveo-mcp-servers/mcp-logs-<server-name>/`
4. **Test server manually**:
   ```bash
   cd /Users/aiveo/mcp-servers/<server_name>
   /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 server.py
   # Should wait for stdin without errors
   ```
5. **Verify dependencies** are installed:
   ```bash
   cd /Users/aiveo/mcp-servers/<server_name>
   /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt
   ```
6. **Check .env file** exists and contains required API keys

### How to verify servers are working

1. **List all configured servers:**
   ```bash
   claude mcp list
   ```

2. **Check for connection status:**
   - ✓ Connected - server is working
   - ✗ Failed to connect - check logs and troubleshoot

3. **Verify tools are available** in Claude Code:
   - Tools should appear with prefix `mcp__<server-name>__<tool-name>`
   - Example: `mcp__google-places-mcp__google_places_nearby_search`

### Removing/Updating Servers

```bash
# Remove a server
claude mcp remove <server-name>

# Update a server (remove and re-add with new configuration)
claude mcp remove <server-name>
claude mcp add <server-name> --type stdio --command <path> --arg <path>
```

## Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## 🎯 Benefits of This Organization

✅ **Single Location** - All MCPs in one centralized directory
✅ **Consistent Naming** - Easy to find and identify with standard `{service}_mcp` pattern
✅ **Easy Management** - Simple to add/remove/update MCPs using `claude mcp` commands
✅ **Clear Structure** - Professional organization with documentation
✅ **Version Control Ready** - Can be backed up/versioned together
✅ **Reusable Paths** - Absolute paths make configuration explicit and reliable

## 📝 Version History

- **2025-11-04**: **CORRECTED** - Removed auto-discovery references; Claude Code requires manual configuration via `claude mcp add`
- **2025-11-04**: Updated all documentation to reflect proper manual MCP configuration process
- **2025-11-04**: Added troubleshooting section for manual configuration issues
- **2025-11-03**: Created README with initial organization structure
- **2025-11-03**: Added naming conventions and organizational structure
- **2025-11-03**: Migrated all MCPs to centralized location with consistent naming
- **2025-11-03**: Enhanced security documentation for `.env` file handling
