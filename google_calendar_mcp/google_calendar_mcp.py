#!/usr/bin/env python3
"""
Google Calendar MCP Server

This MCP server provides comprehensive tools to interact with Google Calendar API,
including listing, creating, updating, deleting events, searching, and checking availability.
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
from zoneinfo import ZoneInfo

import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("google_calendar_mcp")

# Constants
API_BASE_URL = "https://www.googleapis.com/calendar/v3"
CHARACTER_LIMIT = 25000  # Maximum response size in characters

# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"

class TimeRange(str, Enum):
    """Predefined time ranges for listing events."""
    TODAY = "today"
    TOMORROW = "tomorrow"
    THIS_WEEK = "this_week"
    NEXT_WEEK = "next_week"
    THIS_MONTH = "this_month"
    CUSTOM = "custom"

class EventStatus(str, Enum):
    """Event status options."""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"

class AttendeeResponseStatus(str, Enum):
    """Attendee response status options."""
    NEEDS_ACTION = "needsAction"
    DECLINED = "declined"
    TENTATIVE = "tentative"
    ACCEPTED = "accepted"

# Shared utility functions
def _get_api_headers() -> Dict[str, str]:
    """Get authorization headers for Google Calendar API."""
    # Note: In production, this should use proper OAuth2 flow
    # For now, we expect the access token to be in environment variable
    access_token = os.getenv("GOOGLE_CALENDAR_ACCESS_TOKEN")
    if not access_token:
        raise ValueError(
            "GOOGLE_CALENDAR_ACCESS_TOKEN environment variable not set. "
            "Please set it with a valid OAuth2 access token."
        )
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

async def _make_api_request(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Reusable function for all Google Calendar API calls."""
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

            # DELETE returns no content
            if response.status_code == 204:
                return {}

            return response.json()
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
            return "Error: Permission denied. You don't have access to this calendar."
        elif e.response.status_code == 404:
            return "Error: Event or calendar not found. Please check the ID."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}: {e.response.text}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error occurred: {type(e).__name__}: {str(e)}"

def _get_time_range_bounds(time_range: TimeRange, start_date: Optional[str], end_date: Optional[str]) -> tuple[str, str]:
    """Convert time range enum to ISO datetime strings."""
    now = datetime.now(ZoneInfo("UTC"))

    if time_range == TimeRange.TODAY:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif time_range == TimeRange.TOMORROW:
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif time_range == TimeRange.THIS_WEEK:
        # Start from today, go 7 days forward
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    elif time_range == TimeRange.NEXT_WEEK:
        start = (now + timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    elif time_range == TimeRange.THIS_MONTH:
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Get first day of next month
        if now.month == 12:
            end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise ValueError("For CUSTOM time range, both start_date and end_date must be provided")
        # Parse ISO format dates
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    else:
        raise ValueError(f"Invalid time range: {time_range}")

    return start.isoformat(), end.isoformat()

def _format_event_markdown(event: Dict[str, Any]) -> str:
    """Format a single event in Markdown."""
    lines = []

    # Title
    summary = event.get('summary', '(No title)')
    lines.append(f"## {summary}")

    # Time
    start = event.get('start', {})
    end = event.get('end', {})

    if 'dateTime' in start:
        # Timed event
        start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
        lines.append(f"**Time**: {start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')} ({start.get('timeZone', 'UTC')})")
    elif 'date' in start:
        # All-day event
        lines.append(f"**Date**: {start['date']} (All-day)")

    # Event ID
    lines.append(f"**ID**: `{event.get('id')}`")

    # Status
    status = event.get('status', 'confirmed')
    lines.append(f"**Status**: {status}")

    # Description
    if event.get('description'):
        lines.append(f"**Description**: {event['description'][:200]}{'...' if len(event.get('description', '')) > 200 else ''}")

    # Location
    if event.get('location'):
        lines.append(f"**Location**: {event['location']}")

    # Attendees
    attendees = event.get('attendees', [])
    if attendees:
        lines.append(f"**Attendees** ({len(attendees)}):")
        for attendee in attendees[:5]:  # Show first 5
            name = attendee.get('displayName', attendee.get('email', 'Unknown'))
            response = attendee.get('responseStatus', 'needsAction')
            lines.append(f"  - {name} ({response})")
        if len(attendees) > 5:
            lines.append(f"  - ... and {len(attendees) - 5} more")

    # Conference data
    if event.get('hangoutLink'):
        lines.append(f"**Meet Link**: {event['hangoutLink']}")

    lines.append("")  # Empty line between events
    return "\n".join(lines)

def _format_events_response(
    events: List[Dict[str, Any]],
    response_format: ResponseFormat,
    total_count: Optional[int] = None,
    has_more: bool = False
) -> str:
    """Format events list in requested format."""
    if response_format == ResponseFormat.MARKDOWN:
        lines = ["# Google Calendar Events", ""]

        if total_count is not None:
            lines.append(f"Found {total_count} events (showing {len(events)})")
        else:
            lines.append(f"Found {len(events)} events")

        if has_more:
            lines.append("**Note**: More events available. Use pagination to see more.")

        lines.append("")

        if not events:
            lines.append("No events found.")
        else:
            for event in events:
                lines.append(_format_event_markdown(event))

        return "\n".join(lines)
    else:
        # JSON format
        response = {
            "count": len(events),
            "events": events
        }
        if total_count is not None:
            response["total"] = total_count
        if has_more:
            response["has_more"] = has_more

        return json.dumps(response, indent=2)

# Pydantic Models for Input Validation

class ListEventsInput(BaseModel):
    """Input model for listing calendar events."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    calendar_id: str = Field(
        default="primary",
        description="Calendar identifier. Use 'primary' for the user's primary calendar, or specific calendar email address (e.g., 'user@gmail.com')"
    )
    time_range: TimeRange = Field(
        default=TimeRange.THIS_WEEK,
        description="Predefined time range: 'today', 'tomorrow', 'this_week', 'next_week', 'this_month', or 'custom'"
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date/time in ISO 8601 format (e.g., '2024-01-15T10:00:00Z'). Required when time_range='custom'"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date/time in ISO 8601 format (e.g., '2024-01-20T18:00:00Z'). Required when time_range='custom'"
    )
    max_results: Optional[int] = Field(
        default=50,
        description="Maximum number of events to return",
        ge=1,
        le=250
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )

class AttendeeInput(BaseModel):
    """Input model for event attendee."""
    email: str = Field(..., description="Attendee's email address (required)")
    display_name: Optional[str] = Field(default=None, description="Attendee's display name")
    optional: bool = Field(default=False, description="Whether attendance is optional")

class CreateEventInput(BaseModel):
    """Input model for creating a calendar event."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    calendar_id: str = Field(
        default="primary",
        description="Calendar identifier. Use 'primary' for the user's primary calendar"
    )
    summary: str = Field(
        ...,
        description="Event title/summary (required, e.g., 'Team Meeting', 'Dentist Appointment')",
        min_length=1,
        max_length=500
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed event description (supports plain text)",
        max_length=8000
    )
    location: Optional[str] = Field(
        default=None,
        description="Event location (address or place name, e.g., 'Conference Room A', '123 Main St')",
        max_length=500
    )
    start_datetime: str = Field(
        ...,
        description="Start date/time in ISO 8601 format (e.g., '2024-01-15T10:00:00Z' or '2024-01-15T10:00:00+01:00')"
    )
    end_datetime: str = Field(
        ...,
        description="End date/time in ISO 8601 format (e.g., '2024-01-15T11:00:00Z')"
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone for the event (e.g., 'America/New_York', 'Europe/Berlin', 'UTC')"
    )
    attendees: Optional[List[AttendeeInput]] = Field(
        default=None,
        description="List of attendees with email addresses"
    )
    add_meet_link: bool = Field(
        default=False,
        description="Whether to add a Google Meet video conference link"
    )
    send_notifications: bool = Field(
        default=True,
        description="Whether to send email notifications to attendees"
    )
    all_day: bool = Field(
        default=False,
        description="Whether this is an all-day event (if True, times are ignored and dates are used)"
    )

class UpdateEventInput(BaseModel):
    """Input model for updating a calendar event."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    calendar_id: str = Field(
        default="primary",
        description="Calendar identifier"
    )
    event_id: str = Field(
        ...,
        description="Event ID to update (required, obtained from list_events or create_event)"
    )
    summary: Optional[str] = Field(
        default=None,
        description="New event title (leave empty to keep existing)",
        max_length=500
    )
    description: Optional[str] = Field(
        default=None,
        description="New event description (leave empty to keep existing)",
        max_length=8000
    )
    location: Optional[str] = Field(
        default=None,
        description="New location (leave empty to keep existing)",
        max_length=500
    )
    start_datetime: Optional[str] = Field(
        default=None,
        description="New start date/time in ISO 8601 format"
    )
    end_datetime: Optional[str] = Field(
        default=None,
        description="New end date/time in ISO 8601 format"
    )
    timezone: Optional[str] = Field(
        default=None,
        description="New timezone (leave empty to keep existing)"
    )
    status: Optional[EventStatus] = Field(
        default=None,
        description="Event status: 'confirmed', 'tentative', or 'cancelled'"
    )
    send_notifications: bool = Field(
        default=True,
        description="Whether to send email notifications to attendees"
    )

class DeleteEventInput(BaseModel):
    """Input model for deleting a calendar event."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    calendar_id: str = Field(
        default="primary",
        description="Calendar identifier"
    )
    event_id: str = Field(
        ...,
        description="Event ID to delete (required)"
    )
    send_notifications: bool = Field(
        default=True,
        description="Whether to send cancellation notifications to attendees"
    )

class SearchEventsInput(BaseModel):
    """Input model for searching calendar events."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    calendar_id: str = Field(
        default="primary",
        description="Calendar identifier"
    )
    query: str = Field(
        ...,
        description="Search query (searches in summary, description, location, attendee names/emails)",
        min_length=1,
        max_length=200
    )
    max_results: Optional[int] = Field(
        default=50,
        description="Maximum number of results",
        ge=1,
        le=250
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

class CheckAvailabilityInput(BaseModel):
    """Input model for checking calendar availability (freebusy query)."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    calendar_ids: List[str] = Field(
        default=["primary"],
        description="List of calendar IDs to check (e.g., ['primary', 'other@gmail.com'])",
        max_length=50
    )
    start_datetime: str = Field(
        ...,
        description="Start of time range in ISO 8601 format"
    )
    end_datetime: str = Field(
        ...,
        description="End of time range in ISO 8601 format"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

# Tool implementations

@mcp.tool(
    name="gcal_list_events",
    annotations={
        "title": "List Google Calendar Events",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def gcal_list_events(params: ListEventsInput) -> str:
    """
    List events from a Google Calendar within a specified time range.

    This tool retrieves calendar events for various time ranges (today, this week, etc.)
    and can return results in human-readable Markdown or machine-readable JSON format.

    Args:
        params (ListEventsInput): Validated input parameters containing:
            - calendar_id (str): Calendar to query (default: 'primary')
            - time_range (TimeRange): Predefined range or 'custom'
            - start_date (Optional[str]): Custom start (ISO 8601)
            - end_date (Optional[str]): Custom end (ISO 8601)
            - max_results (Optional[int]): Limit results (default: 50, max: 250)
            - response_format (ResponseFormat): 'markdown' or 'json'

    Returns:
        str: Formatted list of events with details including title, time, location,
             attendees, and meet links. Returns error message if request fails.

    Examples:
        - Use when: "Show me my events today"
        - Use when: "What meetings do I have this week?"
        - Use when: "List all events between Jan 15 and Jan 20"
        - Don't use when: Creating or modifying events (use create/update instead)

    Error Handling:
        - Returns authentication error if access token is invalid
        - Returns permission error if calendar access is denied
        - Returns configuration error if custom range missing start/end dates
    """
    try:
        # Get time bounds
        time_min, time_max = _get_time_range_bounds(
            params.time_range,
            params.start_date,
            params.end_date
        )

        # Build API request parameters
        api_params = {
            "timeMin": time_min,
            "timeMax": time_max,
            "maxResults": params.max_results,
            "singleEvents": True,  # Expand recurring events
            "orderBy": "startTime"
        }

        # Make API request
        data = await _make_api_request(
            f"calendars/{params.calendar_id}/events",
            params=api_params
        )

        events = data.get('items', [])

        if not events:
            return f"No events found in the specified time range ({params.time_range.value})."

        # Format and return
        result = _format_events_response(
            events,
            params.response_format,
            total_count=len(events)
        )

        # Check character limit
        if len(result) > CHARACTER_LIMIT:
            truncated_events = events[:max(1, len(events) // 2)]
            result = _format_events_response(
                truncated_events,
                params.response_format,
                total_count=len(events),
                has_more=True
            )
            result += f"\n\n**Note**: Response truncated. Showing {len(truncated_events)} of {len(events)} events."

        return result

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="gcal_create_event",
    annotations={
        "title": "Create Google Calendar Event",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def gcal_create_event(params: CreateEventInput) -> str:
    """
    Create a new event in Google Calendar.

    This tool creates calendar events with full support for attendees, locations,
    descriptions, and optional Google Meet video conferencing links.

    Args:
        params (CreateEventInput): Validated input parameters containing:
            - calendar_id (str): Target calendar (default: 'primary')
            - summary (str): Event title (required)
            - description (Optional[str]): Event details
            - location (Optional[str]): Event location/address
            - start_datetime (str): Start time in ISO 8601 format
            - end_datetime (str): End time in ISO 8601 format
            - timezone (str): Timezone (default: 'UTC')
            - attendees (Optional[List[AttendeeInput]]): List of attendees
            - add_meet_link (bool): Add Google Meet link (default: False)
            - send_notifications (bool): Email attendees (default: True)
            - all_day (bool): All-day event flag (default: False)

    Returns:
        str: Success message with created event details including event ID,
             or error message if creation fails.

    Examples:
        - Use when: "Create a team meeting tomorrow at 2pm"
        - Use when: "Schedule dentist appointment on Friday at 10am"
        - Use when: "Add a lunch meeting with john@company.com next Tuesday"
        - Don't use when: Modifying existing events (use gcal_update_event)

    Error Handling:
        - Returns validation error if start time is after end time
        - Returns permission error if calendar is read-only
        - Returns error if attendee email format is invalid
        - Sends notifications to attendees unless send_notifications=False
    """
    try:
        # Build event object
        event = {
            "summary": params.summary,
        }

        # Add optional fields
        if params.description:
            event["description"] = params.description

        if params.location:
            event["location"] = params.location

        # Handle all-day vs timed events
        if params.all_day:
            # Extract date only (YYYY-MM-DD)
            start_date = params.start_datetime.split('T')[0]
            end_date = params.end_datetime.split('T')[0]
            event["start"] = {"date": start_date}
            event["end"] = {"date": end_date}
        else:
            # Timed event
            event["start"] = {
                "dateTime": params.start_datetime,
                "timeZone": params.timezone
            }
            event["end"] = {
                "dateTime": params.end_datetime,
                "timeZone": params.timezone
            }

        # Add attendees
        if params.attendees:
            event["attendees"] = [
                {
                    "email": attendee.email,
                    **({"displayName": attendee.display_name} if attendee.display_name else {}),
                    "optional": attendee.optional
                }
                for attendee in params.attendees
            ]

        # Add Google Meet link
        if params.add_meet_link:
            event["conferenceData"] = {
                "createRequest": {
                    "requestId": f"meet-{datetime.now().timestamp()}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            }

        # Build API parameters
        api_params = {
            "conferenceDataVersion": 1 if params.add_meet_link else 0,
            "sendUpdates": "all" if params.send_notifications else "none"
        }

        # Make API request
        created_event = await _make_api_request(
            f"calendars/{params.calendar_id}/events",
            method="POST",
            params=api_params,
            json_data=event
        )

        # Format success response
        lines = [
            "# Event Created Successfully",
            "",
            f"**Event ID**: `{created_event.get('id')}`",
            f"**Title**: {created_event.get('summary')}",
        ]

        if created_event.get('start'):
            start = created_event['start']
            if 'dateTime' in start:
                lines.append(f"**Start**: {start['dateTime']}")
            else:
                lines.append(f"**Start**: {start['date']} (All-day)")

        if created_event.get('htmlLink'):
            lines.append(f"**Calendar Link**: {created_event['htmlLink']}")

        if created_event.get('hangoutLink'):
            lines.append(f"**Google Meet**: {created_event['hangoutLink']}")

        if params.attendees and params.send_notifications:
            lines.append(f"\n✉️ Notifications sent to {len(params.attendees)} attendee(s)")

        return "\n".join(lines)

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="gcal_update_event",
    annotations={
        "title": "Update Google Calendar Event",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def gcal_update_event(params: UpdateEventInput) -> str:
    """
    Update an existing Google Calendar event.

    This tool modifies event properties using patch semantics - only specified
    fields are updated, others remain unchanged. Supports updating title, time,
    location, description, and status.

    Args:
        params (UpdateEventInput): Validated input parameters containing:
            - calendar_id (str): Calendar containing the event
            - event_id (str): Event ID to update (required)
            - summary (Optional[str]): New title
            - description (Optional[str]): New description
            - location (Optional[str]): New location
            - start_datetime (Optional[str]): New start time (ISO 8601)
            - end_datetime (Optional[str]): New end time (ISO 8601)
            - timezone (Optional[str]): New timezone
            - status (Optional[EventStatus]): New status (confirmed/tentative/cancelled)
            - send_notifications (bool): Email attendees (default: True)

    Returns:
        str: Success message with updated event details, or error message if update fails.

    Examples:
        - Use when: "Move tomorrow's meeting to 3pm instead of 2pm"
        - Use when: "Change the location of event xyz to Conference Room B"
        - Use when: "Cancel the team standup on Friday"
        - Don't use when: Creating new events (use gcal_create_event)
        - Don't use when: You don't have the event ID (search first)

    Error Handling:
        - Returns 404 error if event ID doesn't exist
        - Returns permission error if you can't modify this event
        - Returns validation error for invalid datetime formats
        - Only updates fields that are explicitly provided (patch semantics)
    """
    try:
        # Build patch object with only provided fields
        patch_data = {}

        if params.summary is not None:
            patch_data["summary"] = params.summary

        if params.description is not None:
            patch_data["description"] = params.description

        if params.location is not None:
            patch_data["location"] = params.location

        if params.status is not None:
            patch_data["status"] = params.status.value

        # Handle datetime updates
        if params.start_datetime or params.end_datetime or params.timezone:
            # Need to get existing event first to preserve start/end structure
            existing_event = await _make_api_request(
                f"calendars/{params.calendar_id}/events/{params.event_id}"
            )

            if params.start_datetime:
                start = existing_event.get('start', {})
                if 'dateTime' in start:
                    patch_data["start"] = {
                        "dateTime": params.start_datetime,
                        "timeZone": params.timezone or start.get('timeZone', 'UTC')
                    }
                else:
                    # All-day event
                    patch_data["start"] = {"date": params.start_datetime.split('T')[0]}

            if params.end_datetime:
                end = existing_event.get('end', {})
                if 'dateTime' in end:
                    patch_data["end"] = {
                        "dateTime": params.end_datetime,
                        "timeZone": params.timezone or end.get('timeZone', 'UTC')
                    }
                else:
                    # All-day event
                    patch_data["end"] = {"date": params.end_datetime.split('T')[0]}

        if not patch_data:
            return "Error: No fields to update. Please specify at least one field to change."

        # Build API parameters
        api_params = {
            "sendUpdates": "all" if params.send_notifications else "none"
        }

        # Make API request (PATCH)
        updated_event = await _make_api_request(
            f"calendars/{params.calendar_id}/events/{params.event_id}",
            method="PATCH",
            params=api_params,
            json_data=patch_data
        )

        # Format success response
        lines = [
            "# Event Updated Successfully",
            "",
            f"**Event ID**: `{updated_event.get('id')}`",
            f"**Title**: {updated_event.get('summary')}",
            f"**Status**: {updated_event.get('status', 'confirmed')}",
        ]

        if updated_event.get('start'):
            start = updated_event['start']
            if 'dateTime' in start:
                lines.append(f"**Start**: {start['dateTime']}")
            else:
                lines.append(f"**Start**: {start['date']} (All-day)")

        if updated_event.get('location'):
            lines.append(f"**Location**: {updated_event['location']}")

        if updated_event.get('htmlLink'):
            lines.append(f"**Calendar Link**: {updated_event['htmlLink']}")

        if params.send_notifications:
            lines.append(f"\n✉️ Update notifications sent to attendees")

        return "\n".join(lines)

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="gcal_delete_event",
    annotations={
        "title": "Delete Google Calendar Event",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def gcal_delete_event(params: DeleteEventInput) -> str:
    """
    Delete an event from Google Calendar.

    This tool permanently removes an event from the calendar. If the event has
    attendees, cancellation notifications can be sent automatically.

    Args:
        params (DeleteEventInput): Validated input parameters containing:
            - calendar_id (str): Calendar containing the event
            - event_id (str): Event ID to delete (required)
            - send_notifications (bool): Send cancellation emails (default: True)

    Returns:
        str: Success confirmation message, or error message if deletion fails.

    Examples:
        - Use when: "Delete tomorrow's dentist appointment"
        - Use when: "Remove the cancelled project meeting from my calendar"
        - Use when: "Cancel and delete the event with ID abc123"
        - Don't use when: You want to cancel but keep the event (use gcal_update_event with status='cancelled')

    Error Handling:
        - Returns 404 error if event doesn't exist
        - Returns permission error if you can't delete this event
        - This operation is permanent and cannot be undone
        - Sends cancellation notifications unless send_notifications=False
    """
    try:
        # Build API parameters
        api_params = {
            "sendUpdates": "all" if params.send_notifications else "none"
        }

        # Make API request (DELETE)
        await _make_api_request(
            f"calendars/{params.calendar_id}/events/{params.event_id}",
            method="DELETE",
            params=api_params
        )

        # Format success response
        lines = [
            "# Event Deleted Successfully",
            "",
            f"**Event ID**: `{params.event_id}` has been permanently removed.",
        ]

        if params.send_notifications:
            lines.append("\n✉️ Cancellation notifications sent to attendees")

        return "\n".join(lines)

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="gcal_search_events",
    annotations={
        "title": "Search Google Calendar Events",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def gcal_search_events(params: SearchEventsInput) -> str:
    """
    Search for events in Google Calendar by keyword.

    This tool searches across event titles, descriptions, locations, and attendee
    names/emails to find matching events. Returns results sorted by start time.

    Args:
        params (SearchEventsInput): Validated input parameters containing:
            - calendar_id (str): Calendar to search (default: 'primary')
            - query (str): Search keywords (required)
            - max_results (Optional[int]): Limit results (default: 50, max: 250)
            - response_format (ResponseFormat): 'markdown' or 'json'

    Returns:
        str: Formatted list of matching events with full details,
             or "No events found" message if no matches.

    Examples:
        - Use when: "Find all meetings with John"
        - Use when: "Search for events about the quarterly review"
        - Use when: "Show me events at Conference Room A"
        - Don't use when: You want events in a specific time range (use gcal_list_events)
        - Don't use when: You already have the event ID (use gcal_list_events or gcal_update_event)

    Error Handling:
        - Returns empty result if no events match the query
        - Search is case-insensitive
        - Partial matches are supported
        - Returns authentication error if access token is invalid
    """
    try:
        # Build API request parameters
        api_params = {
            "q": params.query,
            "maxResults": params.max_results,
            "singleEvents": True,
            "orderBy": "startTime"
        }

        # Make API request
        data = await _make_api_request(
            f"calendars/{params.calendar_id}/events",
            params=api_params
        )

        events = data.get('items', [])

        if not events:
            return f"No events found matching '{params.query}'"

        # Format and return
        result = _format_events_response(
            events,
            params.response_format,
            total_count=len(events)
        )

        # Check character limit
        if len(result) > CHARACTER_LIMIT:
            truncated_events = events[:max(1, len(events) // 2)]
            result = _format_events_response(
                truncated_events,
                params.response_format,
                total_count=len(events),
                has_more=True
            )
            result += f"\n\n**Note**: Response truncated. Showing {len(truncated_events)} of {len(events)} events. Refine your search query for better results."

        return result

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="gcal_check_availability",
    annotations={
        "title": "Check Google Calendar Availability",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def gcal_check_availability(params: CheckAvailabilityInput) -> str:
    """
    Check availability across one or more Google Calendars using freebusy query.

    This tool queries the freebusy status to find when calendars are available
    or busy within a specific time range. Useful for scheduling meetings.

    Args:
        params (CheckAvailabilityInput): Validated input parameters containing:
            - calendar_ids (List[str]): List of calendars to check (default: ['primary'])
            - start_datetime (str): Start of range (ISO 8601 format)
            - end_datetime (str): End of range (ISO 8601 format)
            - response_format (ResponseFormat): 'markdown' or 'json'

    Returns:
        str: Availability information showing busy periods and free slots,
             or error message if query fails.

    Examples:
        - Use when: "Am I free tomorrow between 2pm and 4pm?"
        - Use when: "Check if john@company.com is available next Monday 10-11am"
        - Use when: "Find a free slot this afternoon"
        - Don't use when: You want to see event details (use gcal_list_events)
        - Don't use when: Checking more than a week's availability (too much data)

    Error Handling:
        - Returns permission error if you can't view freebusy for requested calendars
        - Returns empty busy list if calendars are completely free
        - Maximum 50 calendars per request
        - Time range should be reasonable (recommend max 1 week)
    """
    try:
        # Build freebusy request
        request_body = {
            "timeMin": params.start_datetime,
            "timeMax": params.end_datetime,
            "items": [{"id": cal_id} for cal_id in params.calendar_ids]
        }

        # Make API request to freebusy endpoint
        data = await _make_api_request(
            "freeBusy",
            method="POST",
            json_data=request_body
        )

        calendars = data.get('calendars', {})

        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [
                "# Calendar Availability Check",
                "",
                f"**Time Range**: {params.start_datetime} to {params.end_datetime}",
                ""
            ]

            for cal_id in params.calendar_ids:
                cal_data = calendars.get(cal_id, {})
                busy_periods = cal_data.get('busy', [])

                lines.append(f"## Calendar: {cal_id}")

                if not busy_periods:
                    lines.append("✅ **Completely free** during this time range")
                else:
                    lines.append(f"**Busy Periods**: {len(busy_periods)}")
                    for period in busy_periods:
                        start = datetime.fromisoformat(period['start'].replace('Z', '+00:00'))
                        end = datetime.fromisoformat(period['end'].replace('Z', '+00:00'))
                        lines.append(f"  - 🔴 {start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%H:%M')}")

                # Check for errors
                errors = cal_data.get('errors', [])
                if errors:
                    lines.append(f"⚠️ **Errors**: {len(errors)}")
                    for error in errors:
                        lines.append(f"  - {error.get('reason')}: {error.get('domain')}")

                lines.append("")

            return "\n".join(lines)

        else:
            # JSON format
            response = {
                "timeMin": params.start_datetime,
                "timeMax": params.end_datetime,
                "calendars": calendars
            }
            return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_api_error(e)

if __name__ == "__main__":
    mcp.run()
