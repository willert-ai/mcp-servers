# MCP Servers for Claude Code

**Repository Purpose:** Centralized collection of Model Context Protocol (MCP) servers for Claude Code CLI.

**Important:** This is for **Claude Code** (CLI tool), NOT Claude Desktop (desktop application). They use different configuration methods.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [What is MCP?](#what-is-mcp)
3. [Quick Start](#quick-start)
4. [Current MCP Servers](#current-mcp-servers)
5. [Environment Variables & Security](#environment-variables--security)
6. [Configuration Commands](#configuration-commands)
7. [Verification & Usage](#verification--usage)
8. [Creating New MCP Servers](#creating-new-mcp-servers)
9. [Directory Structure & Naming](#directory-structure--naming)
10. [Troubleshooting](#troubleshooting)
11. [Resources](#resources)

---

## Prerequisites

Before using these MCP servers, ensure you have:

### Required
- **Python 3.11.9+** installed via pyenv or system Python
- **pyenv** (recommended for Python version management)
- **Claude Code** installed and configured ([Installation Guide](https://docs.claude.com/claude-code))

### Verify Prerequisites
```bash
# Check Python version
python3 --version
# Should show: Python 3.11.9 or higher

# Check pyenv (if using)
pyenv versions

# Check Claude Code
claude --version
```

### Installing Claude Skills (Optional but Recommended)
To access the MCP builder skill and other useful skills:
```bash
# In Claude Code terminal session
/plugin marketplace add anthropics/skills
```

---

## What is MCP?

**Model Context Protocol (MCP)** is a standard protocol that allows Claude to interact with external tools and services. MCP servers act as bridges between Claude and APIs, databases, or other services.

**Key Concepts:**
- **MCP Server**: A program that exposes tools to Claude via the MCP protocol
- **Tool**: A specific function that Claude can call (e.g., "search Google Places", "create Asana task")
- **Transport**: How Claude communicates with the server (we use `stdio` for Python servers)

**How it Works:**
1. You add an MCP server to Claude Code using `claude mcp add`
2. The server exposes tools that Claude can use
3. When you ask Claude to perform tasks, it can call these tools
4. The tools interact with external services (Google Maps, Asana, etc.)

---

## Quick Start

### Add Your First MCP Server (5 minutes)

```bash
# 1. Navigate to this directory
cd /Users/aiveo/mcp-servers/google_maps_mcp

# 2. Install dependencies
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt

# 3. Create .env file with your API key
cat > .env << 'EOF'
GOOGLE_MAPS_API_KEY=your_api_key_here
EOF

# 4. Add to Claude Code
claude mcp add google-maps-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/google_maps_mcp/server.py

# 5. Verify
claude mcp list
# Should show: ✓ google-maps-mcp - Connected

# 6. Test it!
# In Claude Code, ask: "What's the distance from New York to Boston?"
```

---

## Current MCP Servers

### 1. Asana MCP (`asana-mcp`)

**Purpose:** Complete Asana task management and project organization

**Configuration Required:**
```bash
# In asana_mcp/.env
ASANA_ACCESS_TOKEN=your_personal_access_token_here
ASANA_DEFAULT_WORKSPACE_GID=your_workspace_gid  # Optional but recommended
```

**Get Credentials:**
- Access Token: https://app.asana.com/0/my-apps → Create Personal Access Token
- Workspace GID: From any Asana URL (number after `/0/`)

**Tools Provided (18):**

| Tool | Description | Example Use |
|------|-------------|-------------|
| `asana_list_tasks` | List tasks by assignee, project, completion status | "Show my Asana tasks" |
| `asana_create_task` | Create new task with assignee, due date, project | "Create task: Review Q4 budget" |
| `asana_update_task` | Update task name, assignee, notes, due date | "Update task deadline to Friday" |
| `asana_complete_task` | Mark task as completed | "Complete the budget review task" |
| `asana_search_tasks` | Search tasks by text query | "Find all tasks about marketing" |
| `asana_list_projects` | List all projects in workspace | "What projects do I have?" |
| `asana_get_project_tasks` | Get all tasks in a specific project | "Show tasks in Q4 Planning project" |
| `asana_add_comment` | Add comment to a task | "Add comment: Need more details" |
| `asana_get_task_comments` | View all comments on a task | "Show comments on this task" |
| `asana_list_sections` | List sections in a project | "What sections are in this project?" |
| `asana_move_task_to_section` | Move task to different section | "Move task to In Progress section" |
| `asana_add_subtask` | Add subtask to existing task | "Add subtask: Get approval" |
| `asana_get_task_details` | Get complete task information | "Show full details of this task" |
| `asana_list_tags` | List all tags in workspace | "What tags are available?" |
| `asana_add_tag_to_task` | Add tag to a task | "Tag this as urgent" |
| `asana_set_due_date` | Set or update task due date | "Set due date to next Monday" |
| `asana_assign_task` | Assign task to user | "Assign this to John" |
| `asana_get_user_task_list` | Get user's "My Tasks" GID | "Get my task list ID" |

**Example Usage:**
```
You: "Create an Asana task to review the Q4 budget, due next Friday"
Claude: [Uses asana_create_task to create the task]

You: "What tasks do I have due this week?"
Claude: [Uses asana_list_tasks to show your tasks]
```

---

### 2. Google Calendar MCP (`google-calendar-mcp`)

**Purpose:** Manage Google Calendar events, check availability, search calendars

**Configuration Required:**
```bash
# In google_calendar_mcp/.env
GOOGLE_CALENDAR_ACCESS_TOKEN=your_oauth2_access_token_here
```

**Get Credentials:**
- Requires OAuth2 setup with Google Calendar API
- See: https://developers.google.com/calendar/api/guides/auth

**Tools Provided (6):**

| Tool | Description | Example Use |
|------|-------------|-------------|
| `gcal_list_events` | List events by time range (today, this week, custom) | "What's on my calendar today?" |
| `gcal_create_event` | Create new event with attendees, location, Meet link | "Schedule meeting tomorrow at 2pm" |
| `gcal_update_event` | Update existing event details | "Move tomorrow's meeting to 3pm" |
| `gcal_delete_event` | Delete event from calendar | "Cancel my dentist appointment" |
| `gcal_search_events` | Search events by keyword | "Find all meetings with John" |
| `gcal_check_availability` | Check free/busy status across calendars | "Am I free tomorrow afternoon?" |

**Example Usage:**
```
You: "Create a meeting tomorrow at 2pm for budget review"
Claude: [Uses gcal_create_event to schedule the meeting]

You: "What meetings do I have this week?"
Claude: [Uses gcal_list_events to show your schedule]
```

**Note:** Currently requires OAuth2 token configuration. See `TROUBLESHOOTING_LOG.MD` for setup guidance.

---

### 3. Google Maps MCP (`google-maps-mcp`)

**Purpose:** Location analysis, distance calculations, drive times, place search

**Configuration Required:**
```bash
# In google_maps_mcp/.env
GOOGLE_MAPS_API_KEY=your_api_key_here
```

**Get Credentials:**
- Google Cloud Console: https://console.cloud.google.com
- Enable: Maps JavaScript API, Geocoding API, Distance Matrix API, Places API

**Tools Provided (5):**

| Tool | Description | Example Use |
|------|-------------|-------------|
| `get_distance` | Calculate distance between two locations | "Distance from NYC to Boston?" |
| `get_drive_time` | Calculate drive time with traffic | "How long to drive to airport?" |
| `search_nearby` | Find nearby places by type (hospitals, restaurants) | "Find hospitals near this address" |
| `get_place_details` | Get detailed info about a place | "Details for Memorial Hospital" |
| `validate_address` | Validate and standardize addresses | "Validate this address" |

**Example Usage:**
```
You: "What's the drive time from 123 Main St to the airport?"
Claude: [Uses get_drive_time to calculate with current traffic]

You: "Find restaurants within 5 miles of downtown"
Claude: [Uses search_nearby to find restaurants]
```

---

### 4. Google Places MCP (`google-places-mcp`)

**Purpose:** Property research using Google Maps Platform APIs (Places, Routes, Geocoding)

**Configuration Required:**
```bash
# In google_places_mcp/.env
GOOGLE_MAPS_API_KEY=your_api_key_here
```

**Get Credentials:**
- Same as Google Maps MCP
- Additionally enable: Places API (New), Routes API

**Tools Provided (7):**

| Tool | Description | Example Use |
|------|-------------|-------------|
| `google_places_nearby_search` | Search places by type within radius | "Find all hospitals within 10 miles" |
| `google_places_text_search` | Search places by text query | "Find Memorial Hospital Savannah" |
| `google_places_get_details` | Get comprehensive place details with reviews | "Get details for this hospital" |
| `google_routes_compute_route` | Calculate optimal route with turn-by-turn | "Route from property to downtown" |
| `google_routes_compute_distance_matrix` | Calculate distances between multiple locations | "Compare distances to 5 hospitals" |
| `google_geocoding_geocode` | Convert address to coordinates | "Get coordinates for this address" |
| `google_geocoding_reverse_geocode` | Convert coordinates to address | "What address is at these coordinates?" |

**Example Usage:**
```
You: "Find all hospitals within 15 miles of 123 Main St, Savannah"
Claude: [Uses google_places_nearby_search to find hospitals]

You: "What's the route from the property to downtown with traffic?"
Claude: [Uses google_routes_compute_route for detailed routing]
```

**Note:** This is the more advanced version with Places API (New) and Routes API support.

---

### 5. Medicare Hospital MCP (`medicare-hospital-mcp`)

**Purpose:** Access Medicare hospital quality ratings and compare facilities

**Configuration Required:**
```bash
# No API key needed - uses public Medicare.gov data
```

**Tools Provided (4):**

| Tool | Description | Example Use |
|------|-------------|-------------|
| `get_hospital_rating` | Get overall quality rating (1-5 stars) | "Rating for Memorial Hospital" |
| `search_hospitals` | Search hospitals by location | "Hospitals in Savannah, GA" |
| `get_hospital_quality_measures` | Detailed quality metrics by category | "Quality measures for this hospital" |
| `compare_hospitals` | Side-by-side comparison of multiple hospitals | "Compare these 3 hospitals" |

**Example Usage:**
```
You: "What's the Medicare rating for Memorial Health University Medical Center?"
Claude: [Uses get_hospital_rating to get the rating]

You: "Compare quality ratings for hospitals in Savannah"
Claude: [Uses search_hospitals and compare_hospitals]
```

**Data Source:** Medicare Hospital Compare (data.cms.gov) - Public data, no authentication required.

---

### 6. Perplexity MCP (`perplexity-mcp`)

**Purpose:** AI-powered search and question answering using Perplexity AI

**Configuration Required:**
```bash
# In perplexity_mcp/.env
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

**Get Credentials:**
- Sign up at https://www.perplexity.ai/
- Go to API settings: https://www.perplexity.ai/settings/api
- Generate a new API key

**Tools Provided (4):**

| Tool | Description | Example Use |
|------|-------------|-------------|
| `perplexity_ask` | Q&A with web search and citations | "What's the latest AI news?" |
| `perplexity_search` | Advanced web search with filtering (web/academic/SEC modes) | "Search academic papers about quantum computing" |
| `perplexity_research` | Deep exhaustive research with comprehensive analysis | "Research the history and impact of the Internet" |
| `perplexity_reason` | Logical reasoning without web search | "Explain why 2+2=4 using mathematical principles" |

**Example Usage:**
```
You: "Use Perplexity to explain quantum computing"
Claude: [Uses perplexity_ask to get current information with citations]

You: "Search for recent academic papers on AI safety"
Claude: [Uses perplexity_search with academic mode]

You: "Do deep research on climate change impacts"
Claude: [Uses perplexity_research for exhaustive analysis]

You: "Explain the logic behind this algorithm"
Claude: [Uses perplexity_reason for pure reasoning without web search]
```

**Models Available:**
- **sonar**: Fast, lightweight responses with web search (perplexity_ask)
- **sonar-pro**: Advanced responses with enhanced capabilities (perplexity_search)
- **sonar-deep-research**: Exhaustive research mode (perplexity_research)
- **sonar-reasoning**: Fast reasoning tasks (perplexity_reason)
- **sonar-reasoning-pro**: Premier reasoning with complex logic

**Note:** This server implements the full Perplexity API capabilities. It was initially built as a minimal version to resolve a critical naming issue where the FastMCP server name must exactly match the CLI registration name, then restored to full functionality.

**Key Learning from Setup:**
```python
# CRITICAL: Server name must match CLI name exactly
# CLI registration: claude mcp add perplexity-mcp ...
# Server code:      mcp = FastMCP("perplexity-mcp")  # Must match!
```

---

## Environment Variables & Security

### Critical Requirement: python-dotenv

**Python does NOT automatically load `.env` files.** You must use the `python-dotenv` package.

### Setup Steps

#### 1. Add `python-dotenv` to requirements.txt

Every MCP server using `.env` files MUST include:
```
fastmcp>=0.1.0
httpx>=0.27.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

#### 2. Create .env File

Create `.env` in your server directory:
```bash
# Example: asana_mcp/.env
ASANA_ACCESS_TOKEN=2/1234567890/0987654321:abcdef123456
ASANA_DEFAULT_WORKSPACE_GID=1234567890
```

```bash
# Example: google_maps_mcp/.env
GOOGLE_MAPS_API_KEY=AIzaSyABC123...xyz
```

#### 3. Load .env in Server Code (REQUIRED)

**Every server file MUST include:**
```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()  # ← MUST be called BEFORE os.getenv()

# Now you can access environment variables
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_MAPS_API_KEY not set in .env file")
```

#### 4. Ensure .env is in .gitignore

```bash
# .gitignore
.env
*.env
```

### Security Best Practices

✅ **DO:**
- Store all API keys/tokens in `.env` files
- Add `.env` to `.gitignore` immediately
- Use `python-dotenv` and call `load_dotenv()`
- Create `.env.example` with placeholder values for documentation
- Keep secrets out of version control

❌ **DON'T:**
- Hardcode API keys in server code
- Commit `.env` files to git
- Share API keys in documentation or chat
- Assume `.env` files load automatically

### Why This Matters

**Common Mistake:**
```python
import os
api_key = os.getenv("API_KEY")  # ❌ Returns None - .env not loaded!
```

**Correct Approach:**
```python
from dotenv import load_dotenv
import os

load_dotenv()  # ✅ Loads .env file
api_key = os.getenv("API_KEY")  # ✅ Now returns value from .env
```

**Claude Code does NOT inject environment variables from `.env` files.** Your Python code must explicitly load them.

---

## Configuration Commands

### Add All Servers (Batch Setup)

```bash
cd /Users/aiveo/mcp-servers

# Asana MCP
claude mcp add asana-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/asana_mcp/asana_mcp.py

# Google Calendar MCP
claude mcp add google-calendar-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/google_calendar_mcp/google_calendar_mcp.py

# Google Maps MCP
claude mcp add google-maps-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/google_maps_mcp/server.py

# Google Places MCP
claude mcp add google-places-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/google_places_mcp/server.py

# Medicare Hospital MCP
claude mcp add medicare-hospital-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/medicare_hospital_mcp/server.py

# Perplexity MCP
claude mcp add perplexity-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/perplexity_mcp/server.py

# Verify all servers connected
claude mcp list
```

### Managing Servers

```bash
# List all configured servers
claude mcp list

# Remove a server
claude mcp remove <server-name>

# Update a server (remove and re-add)
claude mcp remove <server-name>
claude mcp add <server-name> --type stdio --command <path> --arg <path>
```

---

## Verification & Usage

### Verify Installation

```bash
# 1. Check servers are connected
claude mcp list

# Expected output:
# ✓ asana-mcp - Connected
# ✓ google-calendar-mcp - Connected
# ✓ google-maps-mcp - Connected
# ✓ google-places-mcp - Connected
# ✓ medicare-hospital-mcp - Connected
# ✓ perplexity-mcp - Connected
```

### Test Tools Are Available

In a Claude Code conversation:

```
You: "List the available MCP tools"
Claude: [Shows all tools from connected MCP servers]
```

Tool names follow this pattern: `mcp__<server-name>__<tool-name>`

**Examples:**
- `mcp__asana-mcp__asana_list_tasks`
- `mcp__google-maps-mcp__get_distance`
- `mcp__google-places-mcp__google_places_nearby_search`

### Test Basic Functionality

Try these example queries:

**Asana:**
```
"Show me my Asana tasks"
"Create an Asana task: Review documentation"
```

**Google Calendar:**
```
"What's on my calendar today?"
"Schedule a meeting tomorrow at 2pm"
```

**Google Maps:**
```
"What's the distance from New York to Boston?"
"Find restaurants near Times Square"
```

**Google Places:**
```
"Find hospitals within 10 miles of Savannah, GA"
"Get details for Memorial Health Hospital"
```

**Medicare Hospital:**
```
"What's the Medicare rating for hospitals in Savannah?"
"Compare quality ratings for Memorial Hospital and St Joseph's"
```

**Perplexity:**
```
"Use Perplexity to explain quantum computing"
"What are the latest AI developments?"
"Use Perplexity to find information about climate change"
```

### Troubleshooting Failed Tests

If tools don't work:

```bash
# 1. Check server logs
ls -la /Users/aiveo/Library/Caches/claude-cli-nodejs/-Users-aiveo-mcp-servers/mcp-logs-<server-name>/

# 2. Verify .env file exists and has values
cat /Users/aiveo/mcp-servers/<server_dir>/.env

# 3. Test .env loading
cd /Users/aiveo/mcp-servers/<server_dir>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Loaded!' if os.getenv('YOUR_KEY') else 'Not loaded')"

# 4. Test server runs without errors
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 server.py
# Should wait for stdin (Ctrl+C to exit)
```

See `TROUBLESHOOTING_LOG.MD` for comprehensive troubleshooting guide.

---

## Creating New MCP Servers

### Using the MCP Builder Skill (Recommended)

The `mcp-builder` skill helps you create high-quality MCP servers following best practices.

#### 1. Install Claude Skills (if not already done)

```bash
# In Claude Code terminal session
/plugin marketplace add anthropics/skills
```

#### 2. Use the MCP Builder Skill

In Claude Code:
```
You: "I want to create a new MCP server for [service name]"
Claude: [Loads mcp-builder skill and guides you through creation]
```

The skill will help you:
- Design the server architecture
- Implement tools following best practices
- Set up proper error handling
- Configure environment variables
- Test the server

#### 3. Manual Creation Template

If creating manually:

```bash
# 1. Create directory
mkdir -p /Users/aiveo/mcp-servers/my_service_mcp
cd /Users/aiveo/mcp-servers/my_service_mcp

# 2. Create server.py
cat > server.py << 'EOF'
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("my_service_mcp")

@mcp.tool()
def my_tool(query: str) -> str:
    """
    Tool description

    Args:
        query: Query parameter

    Returns:
        Result string
    """
    api_key = os.getenv("MY_API_KEY")
    if not api_key:
        return "Error: MY_API_KEY not set in .env file"

    # Your tool logic here
    return f"Result for: {query}"

if __name__ == "__main__":
    mcp.run()
EOF

# 3. Create requirements.txt
cat > requirements.txt << 'EOF'
fastmcp>=0.1.0
httpx>=0.27.0
pydantic>=2.0.0
python-dotenv>=1.0.0
EOF

# 4. Create .env file
cat > .env << 'EOF'
MY_API_KEY=your_api_key_here
EOF

# 5. Create .env.example (for documentation)
cat > .env.example << 'EOF'
MY_API_KEY=your_api_key_here
EOF

# 6. Create README.md
cat > README.md << 'EOF'
# My Service MCP

Description of what this MCP server does.

## Configuration

Add to `.env` file:
```
MY_API_KEY=your_api_key_here
```

## Tools

- `my_tool` - Tool description

## Usage

```
"Use my_tool to query something"
```
EOF

# 7. Add to .gitignore
echo ".env" >> .gitignore

# 8. Install dependencies
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt

# 9. Test server
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 server.py
# Should wait for stdin without errors (Ctrl+C to exit)

# 10. Add to Claude Code
claude mcp add my-service-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/my_service_mcp/server.py

# 11. Verify
claude mcp list
```

### Best Practices for New Servers

1. **Always use `load_dotenv()`** before accessing environment variables
2. **Include comprehensive error messages** in tool responses
3. **Document all tools** with clear docstrings
4. **Create `.env.example`** for documentation
5. **Test thoroughly** before adding to Claude Code
6. **Follow naming conventions** (see below)

---

## Directory Structure & Naming

### Repository Structure

```
mcp-servers/
├── README.md                      ← This file
├── TROUBLESHOOTING_LOG.MD         ← Comprehensive troubleshooting guide
├── .gitignore                     ← Excludes .env files
│
├── asana_mcp/                     ← Directory: underscores + _mcp
│   ├── asana_mcp.py              ← Server implementation
│   ├── requirements.txt           ← Python dependencies
│   ├── .env                       ← API keys (gitignored)
│   ├── .env.example               ← Example configuration
│   └── README.md                  ← Server documentation
│
├── google_calendar_mcp/
│   ├── google_calendar_mcp.py
│   ├── requirements.txt
│   ├── .env
│   └── README.md
│
└── [other servers...]
```

### Naming Conventions

#### Directory Names (File System)
**Pattern:** `{service}_mcp` with **underscores**

**Examples:**
- ✅ `asana_mcp/`
- ✅ `google_calendar_mcp/`
- ✅ `google_maps_mcp/`
- ❌ `google-calendar-mcp/` (hyphens - wrong)
- ❌ `asana/` (missing _mcp - wrong)

#### MCP Server Names (CLI)
**Pattern:** `{service}-mcp` with **hyphens** (kebab-case)

**Examples:**
- ✅ `claude mcp add asana-mcp ...`
- ✅ `claude mcp add google-calendar-mcp ...`
- ❌ `claude mcp add asana_mcp ...` (underscores - wrong)

#### Complete Example

```
Directory:    asana_mcp/
CLI command:  claude mcp add asana-mcp ...
Python code:  FastMCP("asana_mcp")
Tool names:   mcp__asana-mcp__asana_list_tasks
```

**Key Takeaway:**
- **Directories** = `underscores_with_mcp`
- **CLI names** = `hyphens-with-mcp`
- **Tools** = Use CLI name as prefix

---

## Troubleshooting

### Quick Checks

**Server not appearing:**
```bash
# Check if you added it
claude mcp list

# Add with correct absolute paths
claude mcp add my-service-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/my_service_mcp/server.py
```

**"Failed to connect" error:**
```bash
# 1. Verify dependencies installed
cd /Users/aiveo/mcp-servers/<server_dir>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt

# 2. Test server manually
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 server.py
# Should wait for stdin (Ctrl+C to exit)

# 3. Check logs
cat /Users/aiveo/Library/Caches/claude-cli-nodejs/-Users-aiveo-mcp-servers/mcp-logs-<server-name>/latest.log
```

**"API key not configured" error:**
```bash
# 1. Verify .env file exists
cat /Users/aiveo/mcp-servers/<server_dir>/.env

# 2. Check server calls load_dotenv()
grep "load_dotenv" /Users/aiveo/mcp-servers/<server_dir>/server.py

# 3. Test .env loading
cd /Users/aiveo/mcp-servers/<server_dir>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Key:', os.getenv('YOUR_KEY'))"
```

### Comprehensive Troubleshooting

See `/Users/aiveo/mcp-servers/TROUBLESHOOTING_LOG.MD` for:
- Detailed issue analysis
- Root cause explanations
- Step-by-step resolution procedures
- Common mistakes and solutions
- Historical troubleshooting sessions

---

## Resources

### Official Documentation
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP specification
- [Claude Code Docs](https://docs.claude.com/claude-code) - Claude Code guide
- [FastMCP](https://github.com/jlowin/fastmcp) - Python MCP framework
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable management

### API Documentation
- [Asana API](https://developers.asana.com/docs) - Asana developer docs
- [Google Calendar API](https://developers.google.com/calendar) - Calendar API reference
- [Google Maps Platform](https://developers.google.com/maps) - Maps, Places, Routes APIs
- [Medicare Hospital Compare](https://data.cms.gov) - Public Medicare data

### Configuration Locations
- **User Config:** `/Users/aiveo/.claude.json`
- **Debug Logs:** `~/.claude/debug/latest`
- **Server Logs:** `/Users/aiveo/Library/Caches/claude-cli-nodejs/-Users-aiveo-mcp-servers/mcp-logs-<server-name>/`

---

## Key Differences: Claude Code vs Claude Desktop

| Feature | Claude Code (This Repo) | Claude Desktop |
|---------|------------------------|----------------|
| **Type** | CLI tool | Desktop app |
| **Configuration** | `claude mcp add` command | JSON config file |
| **Config Location** | `~/.claude.json` | `~/Library/Application Support/Claude/` |
| **Transport** | `--type stdio` | Various |
| **This Repo** | ✅ Designed for this | ❌ Not compatible |

**Important:** These MCP servers are configured for Claude Code. They will NOT work with Claude Desktop without reconfiguration.

---

## Summary

### Setup Checklist

- [ ] Python 3.11.9+ installed
- [ ] Claude Code installed and working
- [ ] Clone/have this repository
- [ ] Install dependencies for each server: `pip install -r requirements.txt`
- [ ] Create `.env` files with API keys
- [ ] Verify `.env` loading with `load_dotenv()`
- [ ] Add servers with `claude mcp add`
- [ ] Verify with `claude mcp list`
- [ ] Test tools in Claude Code conversation

### Quick Reference

```bash
# Add server
claude mcp add <name> --type stdio --command <python> --arg <script>

# List servers
claude mcp list

# Remove server
claude mcp remove <name>

# Install dependencies
cd /Users/aiveo/mcp-servers/<server_dir>
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt

# Check logs
cat ~/.claude/debug/latest
```

---

**Last Updated:** 2025-11-04
**Maintained By:** Repository Owner
**License:** [Your License]
