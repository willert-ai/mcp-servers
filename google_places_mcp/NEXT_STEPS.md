# Next Steps - Getting Your Google Places MCP Running

Congratulations! Your Google Places MCP server is ready. Here's how to get it up and running.

## 🎯 Quick Start (5 minutes)

### Step 1: Get Your Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/google/maps-apis/)
2. Create a new project (or select existing)
3. Enable these APIs:
   - **Places API (New)** - Click "Enable API" and search for "Places API (New)"
   - **Routes API** - Search and enable
   - **Geocoding API** - Search and enable
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy your API key (keep it secure!)

**💰 Cost**: Google provides $200/month free credit, which covers ~17,000 Places API calls and ~40,000 Routes/Geocoding calls per month.

### Step 2: Configure the MCP Server

```bash
cd ~/google_places_mcp

# Run the setup script
./setup.sh

# OR manually:
pip install -r requirements.txt
cp .env.example .env

# Edit .env and add your API key:
nano .env  # or use any text editor
# Change: GOOGLE_MAPS_API_KEY=your_api_key_here
```

### Step 3: Test the Server

```bash
# Verify installation
python3 -m py_compile server.py

# This should show no errors - the server is ready!
```

### Step 4: Add to Claude Code

Configure the MCP server in Claude Code:

**Option A: Using MCP Settings File (Recommended)**

Create or edit `~/.claude/mcp_settings.json`:

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

**Option B: Using .env File (Alternative)**

If you set up the `.env` file in Step 2, you can use a simpler config:

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

The server will automatically load `GOOGLE_MAPS_API_KEY` from `.env`.

**Important**: Replace `your_actual_api_key_here` with your real API key if using Option A!

### Step 5: Reload Claude Code MCP Servers

After updating the configuration:

1. In Claude Code, use the command to reload MCP servers
2. Or restart your Claude Code session
3. The MCP server will automatically connect

### Step 6: Test It!

In Claude Code, try asking:

```
Find all hospitals within 10 miles of 249 Holland Drive, Savannah, GA 31419
```

Claude Code should use the `google_places_nearby_search` tool and return results!

## 🔍 Verify It's Working

### Check the MCP Connection

In Claude Code, you can verify the MCP server is connected by:
- Checking for the "google-places" server in the MCP server list
- Looking for the available tools when Claude Code starts
- The server should show as "connected" or "running"

### Test Each Tool

Try these prompts to test different tools:

1. **Nearby Search**:
   ```
   Find hotels and restaurants within 5 miles of [your address]
   ```

2. **Text Search**:
   ```
   Search for Memorial Health University Medical Center in Savannah, GA
   ```

3. **Place Details**:
   ```
   Get full details including reviews for the place with ID ChIJN1t_tDeuEmsRUsoyG83frY4
   ```

4. **Route Calculation**:
   ```
   Calculate the driving distance and time from [address A] to [address B]
   ```

5. **Distance Matrix**:
   ```
   Compare distances from [address] to [hospital 1], [hospital 2], and [hospital 3]
   ```

6. **Geocoding**:
   ```
   Validate and geocode the address: 249 Holland Drive, Savannah, GA 31419
   ```

## 🏢 Using for Property Research

Now you can use this MCP server for your research methodology! Here are example workflows:

### Research Workflow 1: Family Accessibility Analysis

```
I'm researching a property at 249 Holland Drive, Savannah, GA 31419.

Please help me analyze:
1. Distance to Savannah/Hilton Head Airport
2. Drive time to downtown Savannah
3. Distance to nearest major highway (I-95)
```

### Research Workflow 2: Healthcare Proximity

```
For the property at 249 Holland Drive, Savannah, GA 31419:

1. Find all hospitals within 10 miles
2. For each hospital, show me the rating, distance, and drive time
3. Get detailed information including reviews for the closest hospital
```

### Research Workflow 3: Community Amenities

```
Research amenities near 249 Holland Drive, Savannah, GA 31419:

1. Find hotels within 5 miles (for visiting families)
2. Find restaurants within 3 miles with ratings above 4.0
3. Locate nearby parks and churches within 5 miles
```

### Research Workflow 4: Batch Distance Analysis

```
I need to compare accessibility for 3 properties to 5 key locations.

Properties:
- 249 Holland Drive, Savannah, GA 31419
- [Property 2 address]
- [Property 3 address]

Key locations:
- Memorial Health Hospital
- Savannah Airport
- Downtown Savannah
- Forsyth Park
- Savannah Mall

Please calculate all distances and create a comparison matrix.
```

## 🐛 Troubleshooting

### "API key not configured" Error

**Problem**: Environment variable not set
**Solution**:
1. Check `.env` file exists and has `GOOGLE_MAPS_API_KEY=your_key`
2. Verify Claude Desktop config has the key in `env` section
3. Restart Claude Desktop after changes

### "API access forbidden" Error

**Problem**: APIs not enabled in Google Cloud Console
**Solution**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/library)
2. Search and enable: "Places API (New)", "Routes API", "Geocoding API"
3. Wait a few minutes for propagation
4. Try again

### "Rate limit exceeded" Error

**Problem**: Too many requests in short time
**Solution**:
1. Wait 1-2 minutes before next request
2. Consider batching queries (use distance_matrix instead of multiple routes)
3. Check usage in [Google Cloud Console](https://console.cloud.google.com/apis/dashboard)

### Server Won't Start

**Problem**: Syntax errors or missing dependencies
**Solution**:
```bash
# Check Python version (need 3.10+)
python3 --version

# Reinstall dependencies
pip install -r requirements.txt

# Verify code compiles
python3 -m py_compile server.py
```

### "No route found" Error

**Problem**: Addresses are invalid or unreachable
**Solution**:
1. Verify addresses with geocoding tool first
2. Check both addresses are in accessible areas
3. Try different travel mode (WALK instead of DRIVE)

## 📊 Monitoring Usage

### Check API Usage

1. Go to [Google Cloud Console - APIs Dashboard](https://console.cloud.google.com/apis/dashboard)
2. Select your project
3. View "Metrics" to see API call counts
4. Set up billing alerts to avoid surprises

### Typical Usage for Property Research

For a single property comprehensive analysis:
- ~10 nearby searches (different place types)
- ~5 text searches (specific places)
- ~10 place details calls
- ~20 route calculations
- ~2 distance matrix calls
- ~5 geocoding calls

**Total**: ~52 API calls per property

**Cost**: Well within free tier ($200/month credit)

## 🚀 Advanced Usage

### Using with Python Scripts

You can also use the MCP server programmatically:

```python
import subprocess
import json

# Start the server
process = subprocess.Popen(
    ['python3', '/Users/aiveo/google_places_mcp/server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Send MCP protocol messages
# (See MCP documentation for details)
```

### Creating Custom Reports

Combine multiple tool calls to create comprehensive area reports. Example prompt:

```
Create a comprehensive property area analysis report for 249 Holland Drive, Savannah, GA 31419 covering:

1. Hospital proximity and quality
2. Family lodging options
3. Dining accessibility
4. Cultural landmarks
5. Transportation access

Format as a markdown report with sections.
```

## 📚 Additional Resources

- **README.md** - Complete documentation
- **QUALITY_REVIEW.md** - Quality assurance verification
- **EVALUATIONS.md** - Test questions and validation
- **Research_Methodology_Area_Analysis.md** - Your original requirements

## 🎉 You're All Set!

Your Google Places MCP server is ready to support your property research workflow. The server implements all the tools needed for your area analysis methodology:

✅ Distance calculations (driving, straight-line)
✅ Drive time estimates (with traffic patterns)
✅ Geocoding (validate addresses)
✅ Nearby search (hospitals, hotels, restaurants, parks, churches)
✅ Place details (ratings, reviews, operating hours)
✅ Batch distance calculations

Start using it in Claude Desktop and let me know if you encounter any issues!

---

**Need Help?**
- Check the README.md troubleshooting section
- Verify API keys are correctly configured
- Test with simple queries first before complex workflows
- Monitor usage in Google Cloud Console

**Happy researching! 🏡🔍**
