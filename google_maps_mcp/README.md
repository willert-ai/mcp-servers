# Google Maps MCP Server

Model Context Protocol (MCP) server for Google Maps API integration, designed for memory care facility location analysis.

## Purpose

This MCP enables automated, programmatic collection of location data for memory care facilities, supporting zero-hallucination research methodology. Built for multi-property analysis.

## Features

### Available Tools

1. **get_distance** - Calculate distance between two locations
2. **get_drive_time** - Calculate drive time with optional traffic consideration
3. **search_nearby** - Find nearby places of specific type (hospitals, parks, restaurants, etc.)
4. **get_place_details** - Get detailed information about a specific place
5. **validate_address** - Validate and standardize addresses using geocoding

### APIs Used

- Google Maps Directions API
- Google Maps Distance Matrix API
- Google Maps Places API
- Google Maps Geocoding API

## Setup

### 1. Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable the following APIs:
   - Directions API
   - Distance Matrix API
   - Places API
   - Geocoding API
4. Create credentials (API Key)
5. Restrict API key to the enabled APIs above (recommended for security)

### 2. Install Dependencies

```bash
cd "/Users/aiveo/Library/CloudStorage/GoogleDrive-fw@feropartners.com/Meine Ablage/07 LEO/project-management/Savannah/MCPs/google-maps-mcp"
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the MCP directory:

```bash
GOOGLE_MAPS_API_KEY=your_api_key_here
```

### 4. Configure Claude Desktop

Add to your Claude Desktop MCP configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "google-maps": {
      "command": "python",
      "args": [
        "/Users/aiveo/Library/CloudStorage/GoogleDrive-fw@feropartners.com/Meine Ablage/07 LEO/project-management/Savannah/MCPs/google-maps-mcp/server.py"
      ],
      "env": {
        "GOOGLE_MAPS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Alternative:** Use the `.env` file by modifying server.py to load from dotenv:

```python
from dotenv import load_dotenv
load_dotenv()  # Add this at the top of server.py
```

### 5. Restart Claude Desktop

Restart Claude Desktop to load the new MCP server.

## Usage Examples

### Example 1: Calculate Distance to Hospital

```python
# Tool: get_distance
# Input:
{
  "origin": "249 Holland Drive, Savannah, GA 31419",
  "destination": "Memorial Health University Medical Center, Savannah, GA",
  "mode": "driving"
}

# Output:
{
  "status": "success",
  "origin": "249 Holland Drive, Savannah, GA 31419",
  "destination": "Memorial Health University Medical Center, Savannah, GA",
  "mode": "driving",
  "distance_miles": 4.23,
  "distance_meters": 6809,
  "distance_formatted": "4.2 mi",
  "source": "Google Maps Distance Matrix API",
  "timestamp": "2025-11-03T14:30:00Z"
}
```

### Example 2: Calculate Drive Time with Traffic

```python
# Tool: get_drive_time
# Input:
{
  "origin": "249 Holland Drive, Savannah, GA 31419",
  "destination": "Savannah/Hilton Head International Airport",
  "time_of_day": "now"
}

# Output:
{
  "status": "success",
  "origin": "249 Holland Drive, Savannah, GA 31419",
  "destination": "Savannah/Hilton Head International Airport",
  "duration_minutes": 18.5,
  "duration_formatted": "19 mins",
  "duration_with_traffic_minutes": 22.3,
  "traffic_delay_minutes": 3.8,
  "distance_miles": 12.7,
  "distance_formatted": "12.7 mi",
  "source": "Google Maps Directions API",
  "timestamp": "2025-11-03T14:30:00Z"
}
```

### Example 3: Find Nearby Hospitals

```python
# Tool: search_nearby
# Input:
{
  "location": "249 Holland Drive, Savannah, GA 31419",
  "place_type": "hospital",
  "radius_miles": 10.0,
  "limit": 5
}

# Output:
{
  "status": "success",
  "search_center": "249 Holland Drive, Savannah, GA 31419",
  "place_type": "hospital",
  "radius_miles": 10.0,
  "total_found": 5,
  "places": [
    {
      "name": "Memorial Health University Medical Center",
      "address": "4700 Waters Ave, Savannah, GA",
      "place_id": "ChIJ...",
      "rating": 3.8,
      "user_ratings_total": 1247,
      "distance_miles": 4.23,
      "drive_time_minutes": 11.2,
      "types": ["hospital", "health", "point_of_interest"]
    },
    {
      "name": "St. Joseph's/Candler Hospital",
      "address": "5353 Reynolds St, Savannah, GA",
      "place_id": "ChIJ...",
      "rating": 3.6,
      "user_ratings_total": 892,
      "distance_miles": 5.67,
      "drive_time_minutes": 13.8,
      "types": ["hospital", "health", "point_of_interest"]
    }
  ],
  "source": "Google Maps Places API",
  "timestamp": "2025-11-03T14:30:00Z"
}
```

### Example 4: Get Hospital Details

```python
# Tool: get_place_details
# Input:
{
  "place_id": "ChIJ..."
}

# Output:
{
  "status": "success",
  "name": "Memorial Health University Medical Center",
  "address": "4700 Waters Avenue, Savannah, GA 31404, USA",
  "phone": "(912) 350-8000",
  "website": "https://memorialhealth.com/",
  "rating": 3.8,
  "user_ratings_total": 1247,
  "types": ["hospital", "health", "point_of_interest", "establishment"],
  "opening_hours": {
    "open_now": true,
    "weekday_text": [
      "Monday: Open 24 hours",
      "Tuesday: Open 24 hours",
      ...
    ]
  },
  "reviews": [
    {
      "author": "John Smith",
      "rating": 5,
      "text": "Excellent emergency care...",
      "time": "2 months ago"
    }
  ],
  "source": "Google Maps Places API",
  "timestamp": "2025-11-03T14:30:00Z"
}
```

### Example 5: Validate Address

```python
# Tool: validate_address
# Input:
{
  "address": "249 Holland Dr, Savannah, GA"
}

# Output:
{
  "status": "success",
  "input_address": "249 Holland Dr, Savannah, GA",
  "formatted_address": "249 Holland Drive, Savannah, GA 31419, USA",
  "latitude": 32.0234567,
  "longitude": -81.1234567,
  "place_id": "ChIJ...",
  "location_type": "ROOFTOP",
  "address_components": {
    "street_number": "249",
    "street": "Holland Drive",
    "city": "Savannah",
    "county": "Chatham County",
    "state": "Georgia",
    "state_code": "GA",
    "zip_code": "31419",
    "country": "United States"
  },
  "source": "Google Maps Geocoding API",
  "timestamp": "2025-11-03T14:30:00Z"
}
```

## Supported Place Types for search_nearby

Common types for memory care facility analysis:

- `hospital` - Hospitals and medical centers
- `pharmacy` - Pharmacies
- `doctor` - Medical practices
- `park` - Parks and gardens
- `restaurant` - Restaurants
- `cafe` - Cafes
- `lodging` - Hotels (for visiting families)
- `airport` - Airports
- `church` - Places of worship
- `library` - Libraries
- `shopping_mall` - Shopping centers

Full list: [Google Places Types](https://developers.google.com/maps/documentation/places/web-service/supported_types)

## Cost & Usage Limits

### Free Tier
- **$200 monthly credit** from Google Cloud
- Applies to all Google Maps APIs

### Estimated Usage per Property Analysis
- Distance calculations: ~50 requests
- Drive time calculations: ~50 requests
- Nearby searches: ~20 requests
- Place details: ~50 requests
- Address validation: ~5 requests

**Total per property:** ~175 requests (~$0.88 at standard rates, covered by free tier)

### API Pricing (after free $200 credit)
- Directions API: $0.005 per request
- Distance Matrix API: $0.005 per element
- Places API (Nearby Search): $0.032 per request
- Places API (Place Details): $0.017 per request
- Geocoding API: $0.005 per request

### Rate Limits
- Directions API: ~40,000 requests/month free
- Places API: ~17,000 requests/month free

**Can analyze:** 100+ properties per month within free tier

## Data Source Documentation

All responses include:
- `source` field indicating which Google Maps API was used
- `timestamp` field with ISO 8601 UTC timestamp
- `status` field indicating success or error

This ensures compliance with zero-hallucination research methodology requiring all facts to be sourced and dated.

## Error Handling

All tools return standardized error responses:

```json
{
  "status": "error",
  "error": "Error description",
  "message": "Human-readable explanation (if available)"
}
```

Common errors:
- `ZERO_RESULTS` - No route found or location not found
- `NOT_FOUND` - Place ID invalid or doesn't exist
- `INVALID_REQUEST` - Missing required parameters
- `OVER_QUERY_LIMIT` - API quota exceeded
- `REQUEST_DENIED` - API key invalid or API not enabled

## Troubleshooting

### "GOOGLE_MAPS_API_KEY environment variable is required"

**Solution:** Add API key to `.env` file or Claude Desktop config

### "REQUEST_DENIED" error

**Solution:**
1. Verify API key is correct
2. Ensure required APIs are enabled in Google Cloud Console
3. Check API key restrictions (if any)

### "OVER_QUERY_LIMIT" error

**Solution:**
1. Check Google Cloud Console for quota usage
2. Wait for quota reset (monthly)
3. Consider enabling billing if free tier exceeded

### MCP server not appearing in Claude Desktop

**Solution:**
1. Check `claude_desktop_config.json` syntax (valid JSON)
2. Verify file paths are correct and absolute
3. Restart Claude Desktop completely
4. Check Claude Desktop logs: `~/Library/Logs/Claude/`

## Development

### Testing the MCP Server

```bash
# Run server directly (for testing)
python server.py

# Test individual functions
python -c "from server import get_distance; print(get_distance('New York, NY', 'Boston, MA'))"
```

### Adding New Functions

1. Add new function with `@mcp.tool()` decorator
2. Include comprehensive docstring with Args, Returns, Example
3. Follow structured response format with status, source, timestamp
4. Update README with usage example

## Related Documentation

- [Research Methodology](../../../Knowledge%20Base/Research_Methodology_Area_Analysis.md)
- [Area Analysis Framework](../../../Knowledge%20Base/Framework_Area_Analysis_Memory_Care.md)

## License

Internal tool for LEO project. Not for public distribution.

## Support

For issues or questions, contact Florian (LEO Voice Agent Pilot).

---

**Created:** November 3, 2025
**Version:** 1.0.0
**Purpose:** Automated location research for memory care facilities (zero-hallucination protocol)
