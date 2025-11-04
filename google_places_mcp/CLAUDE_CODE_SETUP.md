# Google Places MCP - Claude Code Setup Guide

Quick guide to get your Google Places MCP server running in Claude Code.

## 🚀 Quick Setup (2 minutes)

### 1. Get Your Google Maps API Key

Visit [Google Cloud Console](https://console.cloud.google.com/google/maps-apis/) and:
1. Create/select a project
2. Enable these APIs:
   - Places API (New)
   - Routes API
   - Geocoding API
3. Create an API Key under "Credentials"

### 2. Configure Environment

**Option A: Use .env file (Recommended for security)**

```bash
cd ~/google_places_mcp
cp .env.example .env
nano .env  # or use your preferred editor
```

Add your API key:
```
GOOGLE_MAPS_API_KEY=your_actual_api_key_here
```

**Option B: Direct in MCP config (Quick but less secure)**

You'll add the key directly in the MCP settings (shown below).

### 3. Add to Claude Code MCP Settings

Create or edit `~/.claude/mcp_settings.json`:

**If using .env file (Option A - Recommended):**

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

**If using direct config (Option B):**

```json
{
  "mcpServers": {
    "google-places": {
      "command": "python3",
      "args": [
        "/Users/aiveo/google_places_mcp/server.py"
      ],
      "env": {
        "GOOGLE_MAPS_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

### 4. Install Dependencies

```bash
cd ~/google_places_mcp
pip install -r requirements.txt
```

Or use the automated setup:
```bash
./setup.sh
```

### 5. Reload MCP Servers in Claude Code

The server should automatically load when you start/restart Claude Code.

You can verify by checking the available MCP servers in your Claude Code session.

## ✅ Test It!

Try this in Claude Code:

```
Find all hospitals within 10 miles of 249 Holland Drive, Savannah, GA 31419
```

You should see Claude Code using the `google_places_nearby_search` tool!

## 🔧 Troubleshooting

### "API key not configured" error

- **If using .env**: Verify `.env` file exists in `~/google_places_mcp/` with your key
- **If using direct config**: Check `mcp_settings.json` has the correct key in `env` section
- Restart your Claude Code session after changes

### "API access forbidden" error

- Ensure all 3 APIs are enabled in Google Cloud Console
- Wait 2-3 minutes after enabling APIs
- Verify billing is enabled (free tier is fine)

### Server won't start

```bash
# Check Python version (need 3.10+)
python3 --version

# Verify dependencies
pip install -r requirements.txt

# Test compilation
cd ~/google_places_mcp
python3 -m py_compile server.py
```

### Server not showing in Claude Code

1. Check `mcp_settings.json` is valid JSON
2. Verify the path to `server.py` is correct
3. Restart Claude Code completely
4. Check Claude Code logs for error messages

## 📝 Example Queries

Once connected, try these:

**Nearby Search:**
```
Find hotels and restaurants within 5 miles of [address]
```

**Place Details:**
```
Get detailed information including reviews for [place name or ID]
```

**Route Calculation:**
```
Calculate driving distance and time from [origin] to [destination]
```

**Distance Matrix:**
```
Compare distances from [property address] to these 3 hospitals: [list]
```

**Geocoding:**
```
Validate and geocode this address: [full address]
```

## 💡 Pro Tips

1. **Use .env for security** - Don't commit API keys to git
2. **Monitor usage** - Check [Google Cloud Console](https://console.cloud.google.com/apis/dashboard)
3. **Start simple** - Test with basic queries before complex workflows
4. **Use markdown format** - More readable for human review
5. **Batch operations** - Use distance_matrix for multiple calculations

## 📚 Full Documentation

- `README.md` - Complete documentation
- `NEXT_STEPS.md` - Detailed setup guide
- `EVALUATIONS.md` - Test questions
- `PROJECT_SUMMARY.md` - Architecture overview

## 🎯 Ready to Research!

Your Google Places MCP is now ready for property research in Claude Code. All 7 tools are available:

✅ `google_places_nearby_search` - Find amenities by type
✅ `google_places_text_search` - Search by text query
✅ `google_places_get_details` - Get full place info
✅ `google_routes_compute_route` - Calculate routes
✅ `google_routes_compute_distance_matrix` - Batch calculations
✅ `google_geocoding_geocode` - Validate addresses
✅ `google_geocoding_reverse_geocode` - Coordinates to address

Start researching properties immediately! 🏡🔍
