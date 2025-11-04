#!/usr/bin/env python3
"""
Asana MCP Server

This MCP server provides comprehensive tools to interact with Asana API,
including task management, project organization, comments, sections, and tags.
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("asana_mcp")

# Constants
API_BASE_URL = "https://app.asana.com/api/1.0"
CHARACTER_LIMIT = 25000  # Maximum response size in characters

# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"

class TaskSortBy(str, Enum):
    """Sort order for tasks."""
    DUE_DATE = "due_on"
    CREATED_AT = "created_at"
    MODIFIED_AT = "modified_at"
    COMPLETED_AT = "completed_at"

# Shared utility functions
def _get_api_headers() -> Dict[str, str]:
    """Get authorization headers for Asana API."""
    access_token = os.getenv("ASANA_ACCESS_TOKEN")
    if not access_token:
        raise ValueError(
            "ASANA_ACCESS_TOKEN environment variable not set. "
            "Please set it with a valid Personal Access Token."
        )
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def _get_default_workspace_gid() -> Optional[str]:
    """Get default workspace GID from environment variable."""
    return os.getenv("ASANA_DEFAULT_WORKSPACE_GID")

async def _make_api_request(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Reusable function for all Asana API calls."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{API_BASE_URL}/{endpoint}",
                headers=_get_api_headers(),
                params=params,
                json=json_data,
                timeout=30.0
            )
            response.raise_for_status()

            # Asana wraps responses in {"data": ...}
            result = response.json()
            return result.get("data", result)
    except Exception as e:
        raise e

def _handle_api_error(e: Exception) -> str:
    """Consistent error formatting across all tools."""
    if isinstance(e, ValueError):
        return f"Configuration Error: {str(e)}"
    elif isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 400:
            return f"Error: Bad request. {e.response.text}"
        elif e.response.status_code == 401:
            return "Error: Authentication failed. Please check your access token."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access to this resource."
        elif e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}: {e.response.text}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error occurred: {type(e).__name__}: {str(e)}"

def _format_task_markdown(task: Dict[str, Any]) -> str:
    """Format a single task in Markdown."""
    lines = []

    # Title with completion status
    name = task.get('name', '(No name)')
    completed = task.get('completed', False)
    status_icon = "✅" if completed else "⭕"
    lines.append(f"## {status_icon} {name}")

    # Task GID
    lines.append(f"**ID**: `{task.get('gid')}`")

    # Assignee
    assignee = task.get('assignee')
    if assignee:
        lines.append(f"**Assigned to**: {assignee.get('name', 'Unknown')}")
    else:
        lines.append(f"**Assigned to**: Unassigned")

    # Due date
    due_on = task.get('due_on')
    if due_on:
        lines.append(f"**Due**: {due_on}")

    # Completed status
    if completed:
        completed_at = task.get('completed_at', 'Unknown')
        lines.append(f"**Completed**: {completed_at}")

    # Notes/Description
    notes = task.get('notes')
    if notes and notes.strip():
        preview = notes[:200] + "..." if len(notes) > 200 else notes
        lines.append(f"**Notes**: {preview}")

    # Projects
    projects = task.get('projects', [])
    if projects:
        project_names = [p.get('name', 'Unknown') for p in projects[:3]]
        lines.append(f"**Projects**: {', '.join(project_names)}")

    # Tags
    tags = task.get('tags', [])
    if tags:
        tag_names = [t.get('name', 'Unknown') for t in tags[:5]]
        lines.append(f"**Tags**: {', '.join(tag_names)}")

    lines.append("")  # Empty line between tasks
    return "\n".join(lines)

def _format_tasks_response(
    tasks: List[Dict[str, Any]],
    response_format: ResponseFormat,
    title: str = "Asana Tasks"
) -> str:
    """Format tasks list in requested format."""
    if response_format == ResponseFormat.MARKDOWN:
        lines = [f"# {title}", ""]
        lines.append(f"Found {len(tasks)} task(s)")
        lines.append("")

        if not tasks:
            lines.append("No tasks found.")
        else:
            for task in tasks:
                lines.append(_format_task_markdown(task))

        return "\n".join(lines)
    else:
        # JSON format
        return json.dumps({"count": len(tasks), "tasks": tasks}, indent=2)

# Pydantic Models for Input Validation

class ListTasksInput(BaseModel):
    """Input model for listing tasks."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    workspace_gid: Optional[str] = Field(
        default_factory=_get_default_workspace_gid,
        description="Workspace GID to list tasks from (defaults to ASANA_DEFAULT_WORKSPACE_GID env var if set)"
    )
    assignee: Optional[str] = Field(
        default="me",
        description="User GID to filter tasks by assignee. Use 'me' for your tasks (default)"
    )
    project_gid: Optional[str] = Field(
        default=None,
        description="Project GID to filter tasks by project"
    )
    completed_since: Optional[str] = Field(
        default=None,
        description="ISO 8601 date to get completed tasks since this date"
    )
    limit: Optional[int] = Field(
        default=50,
        description="Maximum number of results",
        ge=1,
        le=100
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

class CreateTaskInput(BaseModel):
    """Input model for creating a task."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    name: str = Field(
        ...,
        description="Task name (required, e.g., 'Review Q4 Budget')",
        min_length=1,
        max_length=1024
    )
    notes: Optional[str] = Field(
        default=None,
        description="Task description/notes",
        max_length=65536
    )
    workspace_gid: Optional[str] = Field(
        default_factory=_get_default_workspace_gid,
        description="Workspace GID (defaults to ASANA_DEFAULT_WORKSPACE_GID env var if set)"
    )
    project_gid: Optional[str] = Field(
        default=None,
        description="Project GID to add task to"
    )
    assignee: Optional[str] = Field(
        default=None,
        description="User GID to assign task to (use 'me' for yourself)"
    )
    due_on: Optional[str] = Field(
        default=None,
        description="Due date in YYYY-MM-DD format"
    )
    parent: Optional[str] = Field(
        default=None,
        description="Parent task GID (to create as subtask)"
    )

class UpdateTaskInput(BaseModel):
    """Input model for updating a task."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_gid: str = Field(
        ...,
        description="Task GID to update (required)"
    )
    name: Optional[str] = Field(
        default=None,
        description="New task name",
        max_length=1024
    )
    notes: Optional[str] = Field(
        default=None,
        description="New task notes",
        max_length=65536
    )
    assignee: Optional[str] = Field(
        default=None,
        description="New assignee GID (use 'me' or user GID)"
    )
    due_on: Optional[str] = Field(
        default=None,
        description="New due date in YYYY-MM-DD format"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Mark as completed (true) or incomplete (false)"
    )

class TaskGidInput(BaseModel):
    """Input model for operations requiring only task GID."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_gid: str = Field(
        ...,
        description="Task GID (required)"
    )

class SearchTasksInput(BaseModel):
    """Input model for searching tasks."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    workspace_gid: Optional[str] = Field(
        default_factory=_get_default_workspace_gid,
        description="Workspace GID to search in (defaults to ASANA_DEFAULT_WORKSPACE_GID env var if set)"
    )
    text: Optional[str] = Field(
        default=None,
        description="Text to search for in task names and notes"
    )
    assignee: Optional[str] = Field(
        default=None,
        description="Filter by assignee GID"
    )
    projects: Optional[List[str]] = Field(
        default=None,
        description="List of project GIDs to filter by",
        max_length=10
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Filter by completion status"
    )
    limit: Optional[int] = Field(
        default=50,
        description="Maximum results",
        ge=1,
        le=100
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )

class ListProjectsInput(BaseModel):
    """Input model for listing projects."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    workspace_gid: Optional[str] = Field(
        default_factory=_get_default_workspace_gid,
        description="Workspace GID (defaults to ASANA_DEFAULT_WORKSPACE_GID env var if set)"
    )
    archived: bool = Field(
        default=False,
        description="Include archived projects"
    )
    limit: Optional[int] = Field(
        default=50,
        description="Maximum results",
        ge=1,
        le=100
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )

class ProjectGidInput(BaseModel):
    """Input model for operations requiring project GID."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    project_gid: str = Field(
        ...,
        description="Project GID (required)"
    )
    limit: Optional[int] = Field(
        default=50,
        description="Maximum results",
        ge=1,
        le=100
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )

class AddCommentInput(BaseModel):
    """Input model for adding a comment to a task."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_gid: str = Field(
        ...,
        description="Task GID to add comment to (required)"
    )
    text: str = Field(
        ...,
        description="Comment text (required)",
        min_length=1,
        max_length=65536
    )

class SectionOperationInput(BaseModel):
    """Input model for section operations."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_gid: str = Field(
        ...,
        description="Task GID (required)"
    )
    section_gid: str = Field(
        ...,
        description="Section GID (required)"
    )

class AddSubtaskInput(BaseModel):
    """Input model for adding a subtask."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    parent_task_gid: str = Field(
        ...,
        description="Parent task GID (required)"
    )
    name: str = Field(
        ...,
        description="Subtask name (required)",
        min_length=1,
        max_length=1024
    )
    notes: Optional[str] = Field(
        default=None,
        description="Subtask notes",
        max_length=65536
    )
    assignee: Optional[str] = Field(
        default=None,
        description="Assignee GID"
    )

class TagOperationInput(BaseModel):
    """Input model for tag operations."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_gid: str = Field(
        ...,
        description="Task GID (required)"
    )
    tag_gid: str = Field(
        ...,
        description="Tag GID (required)"
    )

class WorkspaceGidInput(BaseModel):
    """Input model for workspace operations."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    workspace_gid: Optional[str] = Field(
        default_factory=_get_default_workspace_gid,
        description="Workspace GID (defaults to ASANA_DEFAULT_WORKSPACE_GID env var if set)"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )

class SetDueDateInput(BaseModel):
    """Input model for setting due date."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_gid: str = Field(
        ...,
        description="Task GID (required)"
    )
    due_on: str = Field(
        ...,
        description="Due date in YYYY-MM-DD format (required)"
    )

class AssignTaskInput(BaseModel):
    """Input model for assigning a task."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    task_gid: str = Field(
        ...,
        description="Task GID (required)"
    )
    assignee: str = Field(
        ...,
        description="User GID to assign to (use 'me' for yourself)"
    )

class UserGidInput(BaseModel):
    """Input model for user operations."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    user_gid: Optional[str] = Field(
        default="me",
        description="User GID (use 'me' for yourself, default: 'me')"
    )

# Tool implementations

@mcp.tool(
    name="asana_list_tasks",
    annotations={
        "title": "List Asana Tasks",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_list_tasks(params: ListTasksInput) -> str:
    """
    List tasks from Asana workspace or project.

    This tool retrieves tasks based on various filters including assignee,
    project, completion status, and more.

    Args:
        params (ListTasksInput): Validated input parameters containing:
            - workspace_gid (Optional[str]): Workspace to list from
            - assignee (Optional[str]): Filter by assignee (default: 'me')
            - project_gid (Optional[str]): Filter by project
            - completed_since (Optional[str]): Get completed tasks since date
            - limit (Optional[int]): Max results (default: 50, max: 100)
            - response_format (ResponseFormat): 'markdown' or 'json'

    Returns:
        str: Formatted list of tasks with details

    Examples:
        - Use when: "Show me my tasks"
        - Use when: "What tasks are in project X?"
        - Use when: "List completed tasks from this week"
    """
    try:
        # Build API parameters
        api_params = {
            "opt_fields": "name,notes,completed,completed_at,due_on,assignee.name,projects.name,tags.name",
            "limit": params.limit
        }

        if params.assignee:
            api_params["assignee"] = params.assignee

        if params.completed_since:
            api_params["completed_since"] = params.completed_since

        # Determine endpoint
        if params.project_gid:
            endpoint = f"projects/{params.project_gid}/tasks"
        elif params.workspace_gid:
            endpoint = f"workspaces/{params.workspace_gid}/tasks/search"
        else:
            # Default to user's tasks
            endpoint = "tasks"

        # Make API request
        data = await _make_api_request(endpoint, params=api_params)

        # Handle both list and dict responses
        tasks = data if isinstance(data, list) else data.get('data', [])

        if not tasks:
            return "No tasks found."

        # Format response
        result = _format_tasks_response(tasks, params.response_format, "My Tasks")

        # Check character limit
        if len(result) > CHARACTER_LIMIT:
            truncated_tasks = tasks[:max(1, len(tasks) // 2)]
            result = _format_tasks_response(truncated_tasks, params.response_format, "My Tasks (Truncated)")
            result += f"\n\n**Note**: Showing {len(truncated_tasks)} of {len(tasks)} tasks."

        return result

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_create_task",
    annotations={
        "title": "Create Asana Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def asana_create_task(params: CreateTaskInput) -> str:
    """
    Create a new task in Asana.

    This tool creates tasks with optional assignment, due dates, projects,
    and can create subtasks by specifying a parent task.

    Args:
        params (CreateTaskInput): Validated input parameters

    Returns:
        str: Success message with created task details

    Examples:
        - Use when: "Create a task to review the budget"
        - Use when: "Add a new task in project X"
    """
    try:
        # Build task data
        task_data = {
            "data": {
                "name": params.name
            }
        }

        if params.notes:
            task_data["data"]["notes"] = params.notes

        if params.workspace_gid:
            task_data["data"]["workspace"] = params.workspace_gid

        if params.project_gid:
            task_data["data"]["projects"] = [params.project_gid]

        if params.assignee:
            task_data["data"]["assignee"] = params.assignee

        if params.due_on:
            task_data["data"]["due_on"] = params.due_on

        if params.parent:
            task_data["data"]["parent"] = params.parent

        # Make API request
        task = await _make_api_request("tasks", method="POST", json_data=task_data)

        # Format response
        lines = [
            "# Task Created Successfully",
            "",
            f"**Task ID**: `{task.get('gid')}`",
            f"**Name**: {task.get('name')}",
        ]

        if task.get('due_on'):
            lines.append(f"**Due**: {task['due_on']}")

        if task.get('assignee'):
            lines.append(f"**Assigned to**: {task['assignee'].get('name')}")

        return "\n".join(lines)

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_update_task",
    annotations={
        "title": "Update Asana Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_update_task(params: UpdateTaskInput) -> str:
    """
    Update an existing Asana task.

    This tool modifies task properties using patch semantics.
    Only specified fields are updated.

    Args:
        params (UpdateTaskInput): Validated input parameters

    Returns:
        str: Success message with updated task details
    """
    try:
        # Build update data with only provided fields
        update_data = {"data": {}}

        if params.name is not None:
            update_data["data"]["name"] = params.name

        if params.notes is not None:
            update_data["data"]["notes"] = params.notes

        if params.assignee is not None:
            update_data["data"]["assignee"] = params.assignee

        if params.due_on is not None:
            update_data["data"]["due_on"] = params.due_on

        if params.completed is not None:
            update_data["data"]["completed"] = params.completed

        if not update_data["data"]:
            return "Error: No fields to update. Specify at least one field."

        # Make API request
        task = await _make_api_request(
            f"tasks/{params.task_gid}",
            method="PUT",
            json_data=update_data
        )

        # Format response
        lines = [
            "# Task Updated Successfully",
            "",
            f"**Task ID**: `{task.get('gid')}`",
            f"**Name**: {task.get('name')}",
        ]

        if task.get('completed'):
            lines.append(f"**Status**: ✅ Completed")
        else:
            lines.append(f"**Status**: ⭕ Incomplete")

        return "\n".join(lines)

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_complete_task",
    annotations={
        "title": "Complete Asana Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_complete_task(params: TaskGidInput) -> str:
    """
    Mark an Asana task as completed.

    Args:
        params (TaskGidInput): Task GID

    Returns:
        str: Success confirmation
    """
    try:
        update_data = {
            "data": {
                "completed": True
            }
        }

        task = await _make_api_request(
            f"tasks/{params.task_gid}",
            method="PUT",
            json_data=update_data
        )

        return f"✅ Task '{task.get('name')}' marked as completed!"

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_search_tasks",
    annotations={
        "title": "Search Asana Tasks",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_search_tasks(params: SearchTasksInput) -> str:
    """
    Search for tasks in an Asana workspace.

    Args:
        params (SearchTasksInput): Search parameters

    Returns:
        str: Formatted search results
    """
    try:
        if not params.workspace_gid:
            return "Error: workspace_gid is required. Please set ASANA_DEFAULT_WORKSPACE_GID in .env or provide it explicitly."

        api_params = {
            "opt_fields": "name,notes,completed,due_on,assignee.name,projects.name",
            "limit": params.limit
        }

        if params.text:
            api_params["text"] = params.text

        if params.assignee:
            api_params["assignee.any"] = params.assignee

        if params.projects:
            api_params["projects.any"] = ",".join(params.projects)

        if params.completed is not None:
            api_params["completed"] = str(params.completed).lower()

        data = await _make_api_request(
            f"workspaces/{params.workspace_gid}/tasks/search",
            params=api_params
        )

        tasks = data if isinstance(data, list) else data.get('data', [])

        if not tasks:
            return f"No tasks found matching search criteria."

        result = _format_tasks_response(tasks, params.response_format, "Search Results")

        if len(result) > CHARACTER_LIMIT:
            truncated_tasks = tasks[:max(1, len(tasks) // 2)]
            result = _format_tasks_response(truncated_tasks, params.response_format, "Search Results (Truncated)")
            result += f"\n\n**Note**: Showing {len(truncated_tasks)} of {len(tasks)} results."

        return result

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_list_projects",
    annotations={
        "title": "List Asana Projects",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_list_projects(params: ListProjectsInput) -> str:
    """
    List projects in an Asana workspace.

    Args:
        params (ListProjectsInput): Workspace GID and filters

    Returns:
        str: Formatted list of projects
    """
    try:
        if not params.workspace_gid:
            return "Error: workspace_gid is required. Please set ASANA_DEFAULT_WORKSPACE_GID in .env or provide it explicitly."

        api_params = {
            "workspace": params.workspace_gid,
            "archived": str(params.archived).lower(),
            "opt_fields": "name,archived,created_at,modified_at,owner.name",
            "limit": params.limit
        }

        data = await _make_api_request("projects", params=api_params)
        projects = data if isinstance(data, list) else data.get('data', [])

        if not projects:
            return "No projects found."

        if params.response_format == ResponseFormat.MARKDOWN:
            lines = ["# Asana Projects", "", f"Found {len(projects)} project(s)", ""]
            for proj in projects:
                lines.append(f"## {proj.get('name')}")
                lines.append(f"**ID**: `{proj.get('gid')}`")
                if proj.get('owner'):
                    lines.append(f"**Owner**: {proj['owner'].get('name')}")
                if proj.get('archived'):
                    lines.append(f"**Status**: 🗄️ Archived")
                lines.append("")
            return "\n".join(lines)
        else:
            return json.dumps({"count": len(projects), "projects": projects}, indent=2)

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_get_project_tasks",
    annotations={
        "title": "Get Project Tasks",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_get_project_tasks(params: ProjectGidInput) -> str:
    """
    Get all tasks in a specific project.

    Args:
        params (ProjectGidInput): Project GID

    Returns:
        str: Formatted list of tasks in the project
    """
    try:
        api_params = {
            "opt_fields": "name,completed,due_on,assignee.name",
            "limit": params.limit
        }

        data = await _make_api_request(
            f"projects/{params.project_gid}/tasks",
            params=api_params
        )

        tasks = data if isinstance(data, list) else data.get('data', [])

        if not tasks:
            return "No tasks found in this project."

        result = _format_tasks_response(tasks, params.response_format, "Project Tasks")

        if len(result) > CHARACTER_LIMIT:
            truncated_tasks = tasks[:max(1, len(tasks) // 2)]
            result = _format_tasks_response(truncated_tasks, params.response_format, "Project Tasks (Truncated)")
            result += f"\n\n**Note**: Showing {len(truncated_tasks)} of {len(tasks)} tasks."

        return result

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_add_comment",
    annotations={
        "title": "Add Comment to Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def asana_add_comment(params: AddCommentInput) -> str:
    """
    Add a comment to an Asana task.

    Args:
        params (AddCommentInput): Task GID and comment text

    Returns:
        str: Success confirmation
    """
    try:
        comment_data = {
            "data": {
                "text": params.text
            }
        }

        story = await _make_api_request(
            f"tasks/{params.task_gid}/stories",
            method="POST",
            json_data=comment_data
        )

        return f"✅ Comment added to task successfully!"

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_get_task_comments",
    annotations={
        "title": "Get Task Comments",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_get_task_comments(params: TaskGidInput) -> str:
    """
    Get all comments (stories) from an Asana task.

    This tool retrieves the conversation history and comments on a task,
    showing who commented and when.

    Args:
        params (TaskGidInput): Task GID

    Returns:
        str: Formatted list of comments with authors and timestamps

    Examples:
        - Use when: "Show me the comments on task X"
        - Use when: "What's the discussion history on this task?"
        - Use when: "Who commented on task Y?"
    """
    try:
        api_params = {
            "opt_fields": "text,created_at,created_by.name,type"
        }

        data = await _make_api_request(
            f"tasks/{params.task_gid}/stories",
            params=api_params
        )

        stories = data if isinstance(data, list) else data.get('data', [])

        # Filter to only comments (not system stories)
        comments = [s for s in stories if s.get('type') == 'comment']

        if not comments:
            return "No comments found on this task."

        lines = [
            "# Task Comments",
            "",
            f"Found {len(comments)} comment(s)",
            ""
        ]

        for comment in comments:
            author = comment.get('created_by', {}).get('name', 'Unknown')
            created_at = comment.get('created_at', 'Unknown time')
            text = comment.get('text', '(No text)')

            # Format timestamp
            if created_at != 'Unknown time':
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_at = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass

            lines.append(f"## 💬 {author} - {created_at}")
            lines.append(f"{text}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_list_sections",
    annotations={
        "title": "List Project or My Tasks Sections",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_list_sections(params: ProjectGidInput) -> str:
    """
    List all sections in a project or User Task List (My Tasks).

    Note: User Task Lists work the same way as projects for sections.
    You can pass either a project_gid or a user_task_list_gid to this tool.

    Args:
        params (ProjectGidInput): Project GID or User Task List GID

    Returns:
        str: Formatted list of sections

    Examples:
        - Use when: "What sections are in project X?"
        - Use when: "List my My Tasks sections"
        - Use when: "Show me the sections in my task list"
    """
    try:
        # The endpoint works for both projects and user task lists
        # User Task Lists are treated as projects in the API
        data = await _make_api_request(f"projects/{params.project_gid}/sections")
        sections = data if isinstance(data, list) else data.get('data', [])

        if not sections:
            return "No sections found."

        if params.response_format == ResponseFormat.MARKDOWN:
            lines = ["# Sections", "", f"Found {len(sections)} section(s)", ""]
            for section in sections:
                lines.append(f"## {section.get('name')}")
                lines.append(f"**ID**: `{section.get('gid')}`")
                lines.append("")
            return "\n".join(lines)
        else:
            return json.dumps({"count": len(sections), "sections": sections}, indent=2)

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_move_task_to_section",
    annotations={
        "title": "Move Task to Section",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_move_task_to_section(params: SectionOperationInput) -> str:
    """
    Move a task to a different section in a project.

    Args:
        params (SectionOperationInput): Task and section GIDs

    Returns:
        str: Success confirmation
    """
    try:
        move_data = {
            "data": {
                "task": params.task_gid
            }
        }

        await _make_api_request(
            f"sections/{params.section_gid}/addTask",
            method="POST",
            json_data=move_data
        )

        return f"✅ Task moved to section successfully!"

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_add_subtask",
    annotations={
        "title": "Add Subtask",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def asana_add_subtask(params: AddSubtaskInput) -> str:
    """
    Add a subtask to an existing task.

    Args:
        params (AddSubtaskInput): Parent task GID and subtask details

    Returns:
        str: Success message with subtask details
    """
    try:
        subtask_data = {
            "data": {
                "name": params.name,
                "parent": params.parent_task_gid
            }
        }

        if params.notes:
            subtask_data["data"]["notes"] = params.notes

        if params.assignee:
            subtask_data["data"]["assignee"] = params.assignee

        subtask = await _make_api_request(
            "tasks",
            method="POST",
            json_data=subtask_data
        )

        return f"✅ Subtask '{subtask.get('name')}' created (ID: {subtask.get('gid')})"

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_get_task_details",
    annotations={
        "title": "Get Task Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_get_task_details(params: TaskGidInput) -> str:
    """
    Get complete details for a specific task.

    Args:
        params (TaskGidInput): Task GID

    Returns:
        str: Detailed task information
    """
    try:
        api_params = {
            "opt_fields": "name,notes,completed,completed_at,created_at,modified_at,due_on,assignee.name,projects.name,tags.name,parent.name,followers.name"
        }

        task = await _make_api_request(
            f"tasks/{params.task_gid}",
            params=api_params
        )

        lines = [
            "# Task Details",
            "",
            f"## {task.get('name')}",
            f"**ID**: `{task.get('gid')}`",
            ""
        ]

        if task.get('assignee'):
            lines.append(f"**Assigned to**: {task['assignee'].get('name')}")

        if task.get('due_on'):
            lines.append(f"**Due**: {task['due_on']}")

        lines.append(f"**Status**: {'✅ Completed' if task.get('completed') else '⭕ Incomplete'}")

        if task.get('completed_at'):
            lines.append(f"**Completed**: {task['completed_at']}")

        lines.append(f"**Created**: {task.get('created_at')}")
        lines.append(f"**Modified**: {task.get('modified_at')}")

        if task.get('parent'):
            lines.append(f"**Parent Task**: {task['parent'].get('name')}")

        if task.get('projects'):
            proj_names = [p.get('name') for p in task['projects']]
            lines.append(f"**Projects**: {', '.join(proj_names)}")

        if task.get('tags'):
            tag_names = [t.get('name') for t in task['tags']]
            lines.append(f"**Tags**: {', '.join(tag_names)}")

        if task.get('followers'):
            follower_names = [f.get('name') for f in task['followers'][:5]]
            lines.append(f"**Followers**: {', '.join(follower_names)}")

        if task.get('notes'):
            lines.append("")
            lines.append("**Notes**:")
            lines.append(task['notes'])

        return "\n".join(lines)

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_list_tags",
    annotations={
        "title": "List Workspace Tags",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_list_tags(params: WorkspaceGidInput) -> str:
    """
    List all tags in a workspace.

    Args:
        params (WorkspaceGidInput): Workspace GID

    Returns:
        str: Formatted list of tags
    """
    try:
        if not params.workspace_gid:
            return "Error: workspace_gid is required. Please set ASANA_DEFAULT_WORKSPACE_GID in .env or provide it explicitly."

        api_params = {
            "workspace": params.workspace_gid
        }

        data = await _make_api_request("tags", params=api_params)
        tags = data if isinstance(data, list) else data.get('data', [])

        if not tags:
            return "No tags found in this workspace."

        if params.response_format == ResponseFormat.MARKDOWN:
            lines = ["# Workspace Tags", "", f"Found {len(tags)} tag(s)", ""]
            for tag in tags:
                lines.append(f"- **{tag.get('name')}** (`{tag.get('gid')}`)")
            return "\n".join(lines)
        else:
            return json.dumps({"count": len(tags), "tags": tags}, indent=2)

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_add_tag_to_task",
    annotations={
        "title": "Add Tag to Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_add_tag_to_task(params: TagOperationInput) -> str:
    """
    Add a tag to a task.

    Args:
        params (TagOperationInput): Task and tag GIDs

    Returns:
        str: Success confirmation
    """
    try:
        tag_data = {
            "data": {
                "tag": params.tag_gid
            }
        }

        await _make_api_request(
            f"tasks/{params.task_gid}/addTag",
            method="POST",
            json_data=tag_data
        )

        return f"✅ Tag added to task successfully!"

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_set_due_date",
    annotations={
        "title": "Set Task Due Date",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_set_due_date(params: SetDueDateInput) -> str:
    """
    Set or update the due date for a task.

    Args:
        params (SetDueDateInput): Task GID and due date

    Returns:
        str: Success confirmation
    """
    try:
        update_data = {
            "data": {
                "due_on": params.due_on
            }
        }

        task = await _make_api_request(
            f"tasks/{params.task_gid}",
            method="PUT",
            json_data=update_data
        )

        return f"✅ Due date set to {params.due_on} for task '{task.get('name')}'"

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_assign_task",
    annotations={
        "title": "Assign Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_assign_task(params: AssignTaskInput) -> str:
    """
    Assign a task to a user.

    Args:
        params (AssignTaskInput): Task GID and assignee

    Returns:
        str: Success confirmation
    """
    try:
        update_data = {
            "data": {
                "assignee": params.assignee
            }
        }

        task = await _make_api_request(
            f"tasks/{params.task_gid}",
            method="PUT",
            json_data=update_data
        )

        assignee_name = task.get('assignee', {}).get('name', 'user')
        return f"✅ Task '{task.get('name')}' assigned to {assignee_name}"

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="asana_get_user_task_list",
    annotations={
        "title": "Get User Task List",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def asana_get_user_task_list(params: UserGidInput) -> str:
    """
    Get the User Task List (My Tasks) GID for a user.

    This is useful when you need to work with sections in My Tasks,
    as the User Task List GID is required to list or manage sections.

    Args:
        params (UserGidInput): User GID (default: 'me')

    Returns:
        str: User Task List GID and details

    Examples:
        - Use when: "Get my task list ID"
        - Use when: "What's my My Tasks GID?"
        - Use before: Listing sections in My Tasks
    """
    try:
        data = await _make_api_request(f"users/{params.user_gid}/user_task_list")

        lines = [
            "# User Task List",
            "",
            f"**Task List GID**: `{data.get('gid')}`",
            f"**Name**: {data.get('name', 'My Tasks')}",
            f"**Owner**: {data.get('owner', {}).get('name', 'Unknown')}",
            "",
            "💡 **Tip**: Use this GID with `asana_list_sections` to see your My Tasks sections."
        ]

        return "\n".join(lines)

    except Exception as e:
        return _handle_api_error(e)

if __name__ == "__main__":
    mcp.run()
