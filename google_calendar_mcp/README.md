# Google Calendar MCP Server

A Model Context Protocol (MCP) server that provides comprehensive integration with Google Calendar API. This server enables AI assistants to manage calendar events, check availability, and search across calendars.

## Features

### 🔧 Tools Provided

1. **`gcal_list_events`** - List calendar events within time ranges
   - Predefined ranges: today, tomorrow, this week, next week, this month
   - Custom date ranges
   - Pagination support

2. **`gcal_create_event`** - Create new calendar events
   - Support for attendees and email notifications
   - Optional Google Meet video conference links
   - All-day or timed events
   - Timezone support

3. **`gcal_update_event`** - Update existing events
   - Patch semantics (only update specified fields)
   - Change time, location, title, description, status
   - Send notifications to attendees

4. **`gcal_delete_event`** - Delete calendar events
   - Permanent deletion
   - Optional cancellation notifications

5. **`gcal_search_events`** - Search events by keyword
   - Searches titles, descriptions, locations, attendees
   - Case-insensitive partial matching

6. **`gcal_check_availability`** - Check calendar availability
   - Freebusy queries across multiple calendars
   - Find available time slots
   - Useful for meeting scheduling

## Prerequisites

- Python 3.10 or higher
- Google Cloud Project with Calendar API enabled
- OAuth 2.0 credentials

## Setup

### 1. Install Dependencies

```bash
cd google_calendar_mcp
pip install -r requirements.txt
```

### 2. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google Calendar API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials JSON file

### 3. Get Access Token

You need to obtain an OAuth 2.0 access token. Here are two approaches:

#### Option A: Using OAuth Playground (Quick Testing)

1. Go to [Google OAuth Playground](https://developers.google.com/oauthplayground/)
2. Click the gear icon (⚙️) on the right
3. Check "Use your own OAuth credentials"
4. Enter your Client ID and Client Secret
5. In Step 1, select "Calendar API v3" and check:
   - `https://www.googleapis.com/auth/calendar`
6. Click "Authorize APIs"
7. In Step 2, click "Exchange authorization code for tokens"
8. Copy the **Access token** (Note: this expires in ~1 hour)

#### Option B: Using Google Auth Library (Production)

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds.token

# Get and print the access token
token = get_credentials()
print(f"Access Token: {token}")
```

### 4. Set Environment Variable

```bash
export GOOGLE_CALENDAR_ACCESS_TOKEN="your_access_token_here"
```

Or create a `.env` file:
```
GOOGLE_CALENDAR_ACCESS_TOKEN=your_access_token_here
```

## Usage

### Running the Server

#### Stdio Transport (for Claude Desktop):

```bash
python google_calendar_mcp.py
```

#### Installation for Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "python",
      "args": ["/Users/aiveo/google_calendar_mcp/google_calendar_mcp.py"],
      "env": {
        "GOOGLE_CALENDAR_ACCESS_TOKEN": "your_access_token_here"
      }
    }
  }
}
```

Or install using the MCP CLI:

```bash
cd google_calendar_mcp
mcp install google_calendar_mcp.py
```

### Example Usage with Claude

Once installed, you can ask Claude things like:

- "Show me my events today"
- "Create a team meeting tomorrow at 2pm with john@company.com"
- "What's on my calendar this week?"
- "Search for events about the quarterly review"
- "Am I free tomorrow afternoon between 2-4pm?"
- "Move tomorrow's dentist appointment to 3pm"
- "Delete the cancelled project kickoff meeting"

## Tool Details

### Response Formats

All read tools support two response formats:
- **`markdown`** (default): Human-readable formatted output
- **`json`**: Machine-readable structured data

### Time Zones

- All datetime inputs should be in ISO 8601 format
- Examples:
  - `2024-01-15T10:00:00Z` (UTC)
  - `2024-01-15T10:00:00+01:00` (with timezone offset)
  - `2024-01-15T10:00:00-05:00` (EST)

### Calendar IDs

- Use `"primary"` for the user's main calendar
- Use specific email addresses for other calendars (e.g., `"shared@company.com"`)

## Security Considerations

⚠️ **Important Security Notes:**

1. **Access Token Storage**: Never commit access tokens to version control
2. **Token Expiration**: OAuth access tokens expire (typically 1 hour). For production, implement token refresh logic
3. **Scope Limitation**: The server uses `https://www.googleapis.com/auth/calendar` scope for full calendar access
4. **Environment Variables**: Always use environment variables for sensitive credentials

## Troubleshooting

### "Authentication failed" Error
- Check that `GOOGLE_CALENDAR_ACCESS_TOKEN` is set correctly
- Verify the token hasn't expired (get a new one if needed)

### "Permission denied" Error
- Ensure the Google Calendar API is enabled in your project
- Verify OAuth consent screen is configured
- Check that the token has the correct scope

### "Calendar not found" Error
- Verify the calendar ID is correct
- Check that you have access to the specified calendar
- Try using `"primary"` for your main calendar

## Development

### Project Structure

```
google_calendar_mcp/
├── google_calendar_mcp.py    # Main MCP server implementation
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

### Adding New Tools

To add new tools, follow the MCP best practices:

1. Define a Pydantic model for input validation
2. Create a tool function with `@mcp.tool()` decorator
3. Add comprehensive docstring
4. Implement error handling
5. Support multiple response formats where appropriate

## License

This project is provided as-is for use with Google Calendar API and the Model Context Protocol.

## Support

For issues or questions:
- Check the [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- Review [MCP Documentation](https://modelcontextprotocol.io/)
- Ensure your OAuth setup is correct
