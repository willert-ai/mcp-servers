# Asana MCP Server

A comprehensive Model Context Protocol (MCP) Server for Asana with 18 tools for complete task and project management.

## 🔧 Features - 18 Tools

### Task Management (1-5)
1. **`asana_list_tasks`** - List tasks with filters
2. **`asana_create_task`** - Create new tasks
3. **`asana_update_task`** - Edit tasks
4. **`asana_complete_task`** - Mark as completed
5. **`asana_search_tasks`** - Search tasks

### Project Management (6-7)
6. **`asana_list_projects`** - List projects
7. **`asana_get_project_tasks`** - Get all tasks in a project

### Communication (8-9)
8. **`asana_add_comment`** - Add comments
9. **`asana_get_task_comments`** - Read comments

### Section Management (10-11)
10. **`asana_list_sections`** - List project sections
11. **`asana_move_task_to_section`** - Move task to section

### Task Hierarchy (12-13)
12. **`asana_add_subtask`** - Create subtasks
13. **`asana_get_task_details`** - Get complete task details

### Tagging (14-15)
14. **`asana_list_tags`** - List workspace tags
15. **`asana_add_tag_to_task`** - Add tag to task

### Quick Actions (16-17)
16. **`asana_set_due_date`** - Set due date
17. **`asana_assign_task`** - Assign task

### User Task List (18)
18. **`asana_get_user_task_list`** - Get My Tasks GID (for section management)

## 🚀 Setup

### 1. Install Dependencies

```bash
cd ~/asana_mcp
pip install -r requirements.txt
```

### 2. Get Asana Personal Access Token

1. Go to [Asana Developer Console](https://app.asana.com/0/developer-console)
2. Click on **"Personal access tokens"**
3. Click **"+ Create new token"**
4. Enter a name (e.g., "MCP Server")
5. Copy the token (only shown once!)

### 3. Get Your Workspace GID

1. Open Asana in your browser
2. Navigate to any page in your workspace
3. Look at the URL: `https://app.asana.com/0/1205656411889912/home`
4. The number after `/0/` is your workspace GID (e.g., `1205656411889912`)

### 4. Configure Environment Variables

Create a `.env` file in the `asana_mcp` directory:

```bash
ASANA_ACCESS_TOKEN=your_token_here
ASANA_DEFAULT_WORKSPACE_GID=1205656411889912
```

**Note:** The `ASANA_DEFAULT_WORKSPACE_GID` is optional but **highly recommended**. When set, you won't need to specify the workspace GID with every tool call.

### 5. Connect with Claude Code

```bash
cd ~/asana_mcp
claude mcp add --transport stdio --scope user asana \
  --env ASANA_ACCESS_TOKEN=your_token_here \
  -- python /Users/aiveo/asana_mcp/asana_mcp.py
```

## 📋 Usage

After setup, you can use commands in Claude Code like:

```
Show me my Asana tasks
```

```
Create a new task "Budget Review" in project X
```

```
Mark task Y as completed
```

```
Which sections does project Z have?
```

```
Add a comment to task A: "Please review by tomorrow"
```

## 🔑 Important Concepts

### GIDs (Global IDs)
Asana uses GIDs for all resources. You can find them:
- In the URL (e.g., `https://app.asana.com/0/1234567890/1234567890`)
- In task details by right-clicking → "Copy link"
- Through tools like `asana_list_projects` or `asana_list_tasks`

### Workspaces
Most tools require a `workspace_gid`. Find yours:
1. Open Asana in browser
2. The first number in the URL is your Workspace GID

**NEW:** Set `ASANA_DEFAULT_WORKSPACE_GID` in your `.env` file to avoid specifying it every time!

## 📊 Response Formats

All read tools support two formats:
- **`markdown`** (default): Human-readable, formatted
- **`json`**: Machine-readable, structured

## 🔒 Security

- **Never** commit the token to Git
- Token does not expire (but can be revoked)
- Use minimal permissions when possible

## 💡 Tips

1. **Find Workspace GID**: Use Asana URL or browser DevTools
2. **Bulk Operations**: Use Search with filters
3. **Kanban Workflow**: Use Sections for To Do/In Progress/Done
4. **Hierarchy**: Use Subtasks for complex tasks
5. **My Tasks Sections**:
   - Use `asana_get_user_task_list` to get your User Task List GID
   - Use this GID with `asana_list_sections` to see your My Tasks sections
   - User Task Lists work exactly like projects for section management
6. **Default Workspace**: Set `ASANA_DEFAULT_WORKSPACE_GID` in `.env` for convenience

## 🐛 Troubleshooting

### "Authentication failed"
→ Check if `ASANA_ACCESS_TOKEN` is set and valid

### "workspace_gid is required"
→ Either set `ASANA_DEFAULT_WORKSPACE_GID` in `.env` or provide it explicitly in the tool call

### "Resource not found"
→ Check the GID, some resources are workspace-specific

### "Permission denied"
→ Token does not have sufficient permissions for this action

## 📚 Additional Resources

- [Asana API Documentation](https://developers.asana.com/docs)
- [Personal Access Tokens](https://developers.asana.com/docs/personal-access-token)
- [MCP Documentation](https://modelcontextprotocol.io/)
