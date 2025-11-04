# Google Places MCP Server

A comprehensive Model Context Protocol (MCP) server for property research using Google Maps Platform APIs. This server enables automated research of properties and their surrounding areas, providing tools for finding amenities, calculating distances, and analyzing locations.

## Features

### 🏥 Place Search & Discovery
- **Nearby Search**: Find hospitals, hotels, restaurants, parks, churches, and more within a specified radius
- **Text Search**: Search for specific places by name or query (e.g., "Memorial Health Hospital Savannah")
- **Place Details**: Get comprehensive information including ratings, reviews, hours, and amenities

### 🚗 Routes & Distances
- **Route Calculation**: Calculate optimal routes with real-time traffic data
- **Distance Matrix**: Batch calculations for multiple origin-destination pairs
- **Multiple Travel Modes**: Drive, walk, bicycle, transit support

### 📍 Address Validation
- **Geocoding**: Convert addresses to coordinates
- **Reverse Geocoding**: Convert coordinates to addresses

## Installation

### Prerequisites
- Python 3.10 or higher
- Google Maps Platform API Key with the following APIs enabled:
  - Places API (New)
  - Routes API
  - Geocoding API

### Setup Steps

1. **Clone or download this repository**:
   ```bash
   cd ~/google_places_mcp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Google Maps API Key**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/google/maps-apis/)
   - Create a new project or select an existing one
   - Enable the following APIs:
     - Places API (New)
     - Routes API
     - Geocoding API
   - Create credentials (API Key)
   - Copy your API key

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key:
   # GOOGLE_MAPS_API_KEY=your_actual_api_key_here
   ```

5. **Test the server**:
   ```bash
   python server.py --help
   ```

## Configuration with Claude Code

Add this configuration to your Claude Code MCP settings:

**macOS**: `~/.claude/mcp_settings.json`

```json
{
  "mcpServers": {
    "google-places": {
      "command": "python3",
      "args": [
        "/Users/aiveo/google_places_mcp/server.py"
      ],
      "env": {
        "GOOGLE_MAPS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Alternative: Using dotenv**

If you prefer to load from `.env` file, ensure the file is in the same directory as `server.py`:

```bash
cd ~/google_places_mcp
cp .env.example .env
# Edit .env and add: GOOGLE_MAPS_API_KEY=your_actual_key_here
```

Then you can omit the `env` section from the MCP config:

```json
{
  "mcpServers": {
    "google-places": {
      "command": "python3",
      "args": [
        "/Users/aiveo/google_places_mcp/server.py"
      ]
    }
  }
}
```

## Available Tools

### 1. `google_places_nearby_search`
Search for places near a location by type.

**Example**:
```python
{
  "location": "249 Holland Drive, Savannah, GA 31419",
  "place_types": ["hospital", "hotel", "restaurant"],
  "radius_miles": 10,
  "max_results": 20,
  "response_format": "markdown"
}
```

### 2. `google_places_text_search`
Search for places using text query.

**Example**:
```python
{
  "query": "Memorial Health University Medical Center Savannah",
  "location_bias": "Savannah, GA",
  "max_results": 10,
  "response_format": "markdown"
}
```

### 3. `google_places_get_details`
Get comprehensive details about a place using its Place ID.

**Example**:
```python
{
  "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
  "include_reviews": true,
  "max_reviews": 5,
  "response_format": "markdown"
}
```

### 4. `google_routes_compute_route`
Calculate route, distance, and drive time.

**Example**:
```python
{
  "origin": "249 Holland Drive, Savannah, GA 31419",
  "destination": "Savannah/Hilton Head International Airport",
  "travel_mode": "DRIVE",
  "response_format": "markdown"
}
```

### 5. `google_routes_compute_distance_matrix`
Calculate distances for multiple origin-destination pairs.

**Example**:
```python
{
  "origins": ["249 Holland Drive, Savannah, GA 31419", "Downtown Savannah"],
  "destinations": ["Memorial Health Hospital", "Savannah Airport", "Forsyth Park"],
  "travel_mode": "DRIVE",
  "response_format": "markdown"
}
```

### 6. `google_geocoding_geocode`
Convert address to coordinates.

**Example**:
```python
{
  "address": "249 Holland Drive, Savannah, GA 31419",
  "response_format": "markdown"
}
```

### 7. `google_geocoding_reverse_geocode`
Convert coordinates to address.

**Example**:
```python
{
  "latitude": 32.0809,
  "longitude": -81.0912,
  "response_format": "markdown"
}
```

## Use Cases for Property Research

This MCP server is specifically designed to support the research methodology outlined in your area analysis documentation:

### Family Accessibility Research
- Calculate exact distances to downtown, airports, and major highways
- Measure drive times with traffic patterns
- Validate property addresses

### Healthcare Proximity & Quality
- Find hospitals within specified radius
- Get hospital ratings and contact information
- Calculate emergency response distances

### Community Amenities
- Locate nearby hotels for visiting families
- Find restaurants and dining options
- Identify churches, parks, and cultural landmarks

### Area Analysis
- Batch distance calculations for comprehensive area assessment
- Compare multiple properties or facilities
- Generate detailed location reports

## API Costs & Free Tier

Google Maps Platform provides a $200 monthly credit that covers:
- **Places API (New)**: ~17,000 requests/month free
- **Routes API**: ~40,000 requests/month free
- **Geocoding API**: ~40,000 requests/month free

For most property research use cases (even multiple properties), you should stay within the free tier.

## Response Formats

All tools support two response formats:

- **`markdown`** (default): Human-readable formatted text with headers, lists, and emphasis
- **`json`**: Machine-readable structured data for programmatic processing

## Error Handling

The server provides clear, actionable error messages:
- Invalid API key → Instructions to check configuration
- Rate limit exceeded → Suggestion to wait before retrying
- Location not found → Suggestion to verify address format
- API not enabled → Instructions to enable in Google Cloud Console

## Character Limits

Responses are limited to 25,000 characters to prevent overwhelming context windows. If a response exceeds this limit, it will be truncated with a clear message suggesting how to reduce the result size (e.g., reduce radius, fewer results, disable reviews).

## Security Best Practices

- **Never commit API keys to version control**
- Store API keys in environment variables or `.env` file
- Add `.env` to `.gitignore`
- Use API key restrictions in Google Cloud Console:
  - Restrict to specific APIs
  - Restrict by IP address (if hosting remotely)
  - Set usage quotas to prevent unexpected charges

## Troubleshooting

### "API key not configured" error
- Verify `GOOGLE_MAPS_API_KEY` is set in your environment or `.env` file
- Check that the key is valid and not expired

### "API access forbidden" error
- Ensure all required APIs are enabled in Google Cloud Console
- Check that your API key has permission to access these APIs
- Verify billing is enabled on your Google Cloud project

### "No route found" error
- Verify both addresses are valid and accessible
- Check that the travel mode is appropriate for the route
- Some locations may not be reachable by certain modes

### Server won't start
- Verify Python version: `python --version` (should be 3.10+)
- Check all dependencies are installed: `pip install -r requirements.txt`
- Run with `python -m py_compile server.py` to check for syntax errors

## Development

### Project Structure
```
google_places_mcp/
├── server.py           # Main MCP server implementation
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── .env                # Your actual environment variables (gitignored)
└── README.md           # This file
```

### Adding Custom Tools

To add new tools, follow the pattern in `server.py`:

1. Define a Pydantic input model with validation
2. Use `@mcp.tool()` decorator with annotations
3. Implement comprehensive docstring
4. Use shared utility functions for API calls
5. Support both markdown and JSON response formats
6. Implement character limit checking

## License

This MCP server is provided as-is for use with Google Maps Platform APIs. Ensure compliance with [Google Maps Platform Terms of Service](https://cloud.google.com/maps-platform/terms).

## Support

For issues with:
- **This MCP server**: Check the troubleshooting section above
- **Google Maps APIs**: See [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- **MCP Protocol**: See [Model Context Protocol Documentation](https://modelcontextprotocol.io)

## Changelog

### Version 1.0.0 (2025-11-03)
- Initial release
- Implements 7 core tools for property research
- Supports Places API (New), Routes API, and Geocoding API
- Comprehensive error handling and validation
- Markdown and JSON response formats
- Character limit enforcement
