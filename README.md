# MCP Servers Directory

This directory contains Model Context Protocol (MCP) servers for Claude Code auto-discovery.

## Auto-Discovery Requirement

**IMPORTANT**: For Claude Code to automatically discover and load MCP servers from this directory, each server **MUST** include an `mcp.json` configuration file in its root directory.

### Required: `mcp.json` Configuration File

Every MCP server in this directory must have an `mcp.json` file with the following structure:

```json
{
  "name": "service-name-mcp",
  "description": "Brief description of what this MCP server does",
  "command": "python3",
  "args": ["server.py"],
  "env": {}
}
```

### Configuration Fields

- **name** (required): Unique identifier for the MCP server. Must use kebab-case with `-mcp` suffix (e.g., `"asana-mcp"`, `"google-calendar-mcp"`)
- **description** (required): Clear description of the server's functionality
- **command** (required): Command to execute the server (e.g., `python3`, `node`, `uvx`)
- **args** (required): Array of arguments passed to the command (e.g., `["server.py"]`)
- **env** (required): Environment variables object. Use empty `{}` when loading from `.env` file (recommended for security)

### Example Directory Structure

```
mcp-servers/
├── README.md (this file)
├── google_places_mcp/
│   ├── mcp.json          ← REQUIRED for auto-discovery
│   ├── server.py
│   ├── requirements.txt
│   ├── .env
│   └── README.md
├── asana_mcp/
│   ├── mcp.json          ← REQUIRED for auto-discovery
│   ├── asana_mcp.py
│   ├── requirements.txt
│   └── README.md
└── your_new_mcp/
    ├── mcp.json          ← REQUIRED for auto-discovery
    ├── server.py
    └── ...
```

## Creating a New MCP Server

When creating a new MCP server in this directory:

1. **Create your MCP server directory** with your server code
2. **Create `mcp.json`** in the server's root directory with proper configuration
3. **Restart Claude Code** to auto-discover the new server
4. **Verify** the server tools appear with prefix `mcp__<server-name>__*`

### Step-by-Step Example

```bash
# 1. Create new MCP server directory (use underscores + _mcp suffix)
mkdir -p ~/mcp-servers/my_service_mcp

# 2. Add your server code
cd ~/mcp-servers/my_service_mcp
# ... create server.py, requirements.txt, etc.

# 3. Create .env file for API keys/tokens (if needed)
cat > .env << 'EOF'
API_KEY=your_secret_key_here
EOF

# 4. Create mcp.json (name uses hyphens + -mcp suffix)
cat > mcp.json << 'EOF'
{
  "name": "my-service-mcp",
  "description": "Description of what my server does",
  "command": "python3",
  "args": ["server.py"],
  "env": {}
}
EOF

# 5. Restart Claude Code to load the new server
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

### Server not appearing after restart

1. **Check `mcp.json` exists** in the server's root directory
2. **Validate JSON syntax** using `cat mcp.json | python3 -m json.tool`
3. **Check file paths** in `args` field are correct
4. **Verify command** in `command` field is available (`which python3`)
5. **Restart Claude Code** completely

### Server appears but tools don't work

1. **Check server logs** for errors
2. **Verify dependencies** are installed (`pip install -r requirements.txt`)
3. **Check environment variables** are set correctly
4. **Test server manually**: `python3 server.py` (if applicable)

### How to verify auto-discovery worked

After restarting Claude Code, your tools should appear with the naming pattern:
- `mcp__<server-name>__<tool-name>`

Example: `mcp__google-places-mcp__google_places_nearby_search`

Note: The tool prefix uses the **mcp.json name** (with hyphens), not the directory name.

## Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## 🎯 Benefits of This Organization

✅ **Single Location** - All MCPs in one centralized directory
✅ **Auto-Discovery** - Claude Code automatically finds and loads all MCPs with `mcp.json`
✅ **Consistent Naming** - Easy to find and identify with standard `{service}_mcp` pattern
✅ **Easy Management** - Simple to add/remove/update MCPs
✅ **Clear Structure** - Professional organization with documentation
✅ **Version Control Ready** - Can be backed up/versioned together

## 📝 Version History

- **2025-11-03**: Created README with auto-discovery requirements
- **2025-11-03**: Added naming conventions and organizational structure
- **2025-11-03**: Migrated all MCPs to centralized location with consistent naming
- **2025-11-03**: Standardized all mcp.json names with `-mcp` suffix (kebab-case)
- **2025-11-03**: Enhanced security documentation for `.env` file handling
- **2025-11-03**: Clarified two-part naming system (directories vs mcp.json names)
