# Changelog - Asana MCP Server

## 2025-11-04 - Default Workspace GID Support

### New Features

#### Automatic Workspace GID Configuration
- **Environment Variable:** `ASANA_DEFAULT_WORKSPACE_GID` in `.env` file
- Workspace GID no longer needs to be specified with every tool call
- Automatic use of default value from environment variable
- Affected tools:
  - `asana_create_task`
  - `asana_list_tasks`
  - `asana_search_tasks`
  - `asana_list_projects`
  - `asana_list_tags`

### Improvements

#### Simplified User Experience
- No manual workspace GID input required anymore
- One-time configuration in `.env` file
- Fallback to explicit specification still possible
- Helpful error message when neither default nor explicit GID is provided

### Setup
```bash
# Add to .env file:
ASANA_ACCESS_TOKEN=your_token_here
ASANA_DEFAULT_WORKSPACE_GID=1205656411889912
```

### Example Usage

**Before:**
```python
asana_create_task(
    name="Transfer payment to NHS",
    workspace_gid="1205656411889912",  # Had to always specify
    due_on="2025-11-04"
)
```

**After:**
```python
asana_create_task(
    name="Transfer payment to NHS",
    # workspace_gid is automatically read from .env
    due_on="2025-11-04"
)
```

---

## 2025-11-03 - My Tasks Section Support

### New Features

#### Tool 18: `asana_get_user_task_list`
- New tool to retrieve User Task List GID
- Enables working with My Tasks sections
- Default parameter: `user_gid="me"` for current user

### Improvements

#### `asana_list_sections` - Extended Support
- Now supports both projects and User Task Lists (My Tasks)
- Updated documentation and examples
- Title changed to "List Project or My Tasks Sections"

### Important Insights

**User Task Lists and Sections:**
- User Task Lists work like regular projects in the Asana API
- The endpoint `GET /projects/{user_task_list_gid}/sections` works with User Task List GIDs
- There is NO separate `/user_task_lists/{gid}/sections` endpoint
- Sections in My Tasks can be managed just like project sections

### Workflow for My Tasks Sections

1. **Retrieve User Task List GID:**
   ```
   asana_get_user_task_list(user_gid="me")
   ```

2. **List sections:**
   ```
   asana_list_sections(project_gid=<user_task_list_gid>)
   ```

3. **Move task to section:**
   ```
   asana_move_task_to_section(task_gid=<task_gid>, section_gid=<section_gid>)
   ```

### Example Usage

```python
# 1. Get My Tasks GID
user_task_list_gid = "1205656411889926"

# 2. Display sections
sections = [
    {"gid": "1205656411889940", "name": "🔎 Today"},
    {"gid": "1205656411889941", "name": "📆 This week"},
    {"gid": "1211206976525042", "name": "🌙 This month"},
    # ... more sections
]

# 3. Move task to "Today" section
asana_move_task_to_section(
    task_gid="1211819567509721",
    section_gid="1205656411889940"
)
```

### API Documentation References

- [Asana API: User Task Lists](https://developers.asana.com/reference/getusertasklistforuser)
- [Asana API: Sections](https://developers.asana.com/reference/getsectionsforproject)
- [Forum: My Tasks Section Changes](https://forum.asana.com/t/upcoming-changes-coming-to-my-tasks-in-asana-and-the-api-breaking-changes/109717)

### Tool Count

- **Before:** 17 Tools
- **Now:** 18 Tools
