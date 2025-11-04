#!/usr/bin/env python3
"""
OAuth 2.0 Token Helper for Google Calendar MCP Server

This script helps you obtain and refresh OAuth 2.0 tokens for Google Calendar API.
It handles the OAuth flow and stores the refresh token for future use.

Usage:
    1. Download your OAuth credentials from Google Cloud Console
    2. Save them as 'credentials.json' in the same directory
    3. Run: python get_token.py
    4. Follow the browser authentication flow
    5. Copy the access token to use with the MCP server
"""

import os
import json
import pickle
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    print("❌ Error: Google auth libraries not installed.")
    print("\nInstall them with:")
    print("  pip install google-auth-oauthlib google-auth-httplib2")
    exit(1)

# Scopes required for full calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Files for storing credentials and tokens
CREDENTIALS_FILE = 'credentials.json'
TOKEN_PICKLE_FILE = 'token.pickle'


def get_credentials():
    """
    Get valid OAuth 2.0 credentials, handling refresh if needed.

    Returns:
        Credentials object with valid access token
    """
    creds = None
    token_path = Path(TOKEN_PICKLE_FILE)
    credentials_path = Path(CREDENTIALS_FILE)

    # Check if credentials.json exists
    if not credentials_path.exists():
        print(f"❌ Error: '{CREDENTIALS_FILE}' not found.")
        print("\nSteps to get credentials.json:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project or select existing one")
        print("3. Enable Google Calendar API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download and save as 'credentials.json' in this directory")
        exit(1)

    # Load existing token if available
    if token_path.exists():
        print("📂 Loading existing token...")
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Check if credentials are valid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully!")
            except Exception as e:
                print(f"❌ Error refreshing token: {e}")
                print("   Starting new authentication flow...")
                creds = None

        # Need new authentication
        if not creds:
            print("\n🔐 Starting OAuth authentication flow...")
            print("   Your browser will open for authentication.")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                print("✅ Authentication successful!")
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                exit(1)

        # Save the credentials for future use
        print(f"💾 Saving credentials to '{TOKEN_PICKLE_FILE}'...")
        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return creds


def print_token_info(creds):
    """Print token information and usage instructions."""
    print("\n" + "="*70)
    print("✅ ACCESS TOKEN OBTAINED SUCCESSFULLY!")
    print("="*70)
    print(f"\n📝 Access Token:\n{creds.token}\n")

    if creds.expiry:
        print(f"⏰ Expires at: {creds.expiry}")

    print("\n" + "="*70)
    print("🚀 NEXT STEPS")
    print("="*70)

    print("\n1. Set the environment variable:")
    print(f'   export GOOGLE_CALENDAR_ACCESS_TOKEN="{creds.token}"')

    print("\n2. Or add to your shell profile (~/.zshrc or ~/.bashrc):")
    print(f'   echo \'export GOOGLE_CALENDAR_ACCESS_TOKEN="{creds.token}"\' >> ~/.zshrc')

    print("\n3. Or use the token directly in Claude Desktop config:")
    print('   Edit: ~/Library/Application Support/Claude/claude_desktop_config.json')
    print('   Add under "google-calendar" > "env":')
    print(f'   "GOOGLE_CALENDAR_ACCESS_TOKEN": "{creds.token}"')

    print("\n4. Test the MCP server:")
    print("   python google_calendar_mcp.py")

    print("\n" + "="*70)
    print("💡 TIP: This token will be auto-refreshed next time you run this script!")
    print("="*70 + "\n")


def save_env_file(creds):
    """Save token to .env file for easy loading."""
    env_file = Path('.env')

    # Read existing .env if it exists
    env_vars = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value

    # Update token
    env_vars['GOOGLE_CALENDAR_ACCESS_TOKEN'] = creds.token

    # Write back
    with open(env_file, 'w') as f:
        f.write("# Google Calendar MCP Server Configuration\n")
        f.write("# Generated by get_token.py\n\n")
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    print(f"✅ Token saved to '.env' file")


def main():
    """Main function to run the token helper."""
    print("="*70)
    print("🔐 Google Calendar OAuth Token Helper")
    print("="*70 + "\n")

    try:
        # Get or refresh credentials
        creds = get_credentials()

        # Print token info
        print_token_info(creds)

        # Save to .env file
        save_env_file(creds)

        # Test API access
        print("\n🧪 Testing API access...")
        import httpx
        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json"
        }

        try:
            response = httpx.get(
                "https://www.googleapis.com/calendar/v3/users/me/calendarList",
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            calendars = response.json()

            print(f"✅ API test successful! Found {len(calendars.get('items', []))} calendar(s)")

            if calendars.get('items'):
                print("\n📅 Your calendars:")
                for cal in calendars['items'][:5]:  # Show first 5
                    print(f"   - {cal.get('summary')} ({cal.get('id')})")

        except httpx.HTTPError as e:
            print(f"⚠️  API test failed: {e}")
            print("   The token may not have proper permissions.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)


if __name__ == '__main__':
    main()
