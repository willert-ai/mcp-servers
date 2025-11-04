"""
Test script for Google Maps MCP

This script tests all MCP functions to verify they work correctly
before integrating with Claude Desktop.

Setup:
1. Copy .env.example to .env
2. Add your Google Maps API key to .env
3. Install dependencies: pip install -r requirements.txt
4. Run: python test_mcp.py
"""

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Check if API key is set
if not os.getenv("GOOGLE_MAPS_API_KEY"):
    print("❌ ERROR: GOOGLE_MAPS_API_KEY not found in environment")
    print("Please copy .env.example to .env and add your API key")
    exit(1)

# Import server functions
from server import (
    get_distance,
    get_drive_time,
    search_nearby,
    get_place_details,
    validate_address
)

print("=" * 60)
print("GOOGLE MAPS MCP TEST SUITE")
print("=" * 60)
print()

# Test facility address
FACILITY_ADDRESS = "249 Holland Drive, Savannah, GA 31419"

# Test 1: Validate Address
print("TEST 1: Validate Address")
print("-" * 60)
result = validate_address(FACILITY_ADDRESS)
if result['status'] == 'success':
    print("✅ PASS")
    print(f"   Formatted: {result['formatted_address']}")
    print(f"   Coordinates: {result['latitude']}, {result['longitude']}")
    print(f"   City: {result['address_components']['city']}")
    print(f"   State: {result['address_components']['state']}")
else:
    print(f"❌ FAIL: {result.get('error')}")
print()

# Test 2: Calculate Distance
print("TEST 2: Calculate Distance to Hospital")
print("-" * 60)
result = get_distance(
    FACILITY_ADDRESS,
    "Memorial Health University Medical Center, Savannah, GA",
    "driving"
)
if result['status'] == 'success':
    print("✅ PASS")
    print(f"   Distance: {result['distance_miles']} miles")
    print(f"   Formatted: {result['distance_formatted']}")
else:
    print(f"❌ FAIL: {result.get('error')}")
print()

# Test 3: Calculate Drive Time
print("TEST 3: Calculate Drive Time to Airport")
print("-" * 60)
result = get_drive_time(
    FACILITY_ADDRESS,
    "Savannah/Hilton Head International Airport",
    "now"
)
if result['status'] == 'success':
    print("✅ PASS")
    print(f"   Duration: {result['duration_minutes']} minutes")
    print(f"   Distance: {result['distance_miles']} miles")
    if 'duration_with_traffic_minutes' in result:
        print(f"   With traffic: {result['duration_with_traffic_minutes']} minutes")
        print(f"   Traffic delay: {result['traffic_delay_minutes']} minutes")
else:
    print(f"❌ FAIL: {result.get('error')}")
print()

# Test 4: Search Nearby Hospitals
print("TEST 4: Search Nearby Hospitals")
print("-" * 60)
result = search_nearby(
    FACILITY_ADDRESS,
    "hospital",
    10.0,
    3
)
if result['status'] == 'success':
    print("✅ PASS")
    print(f"   Found: {result['total_found']} hospitals")
    for i, place in enumerate(result['places'], 1):
        print(f"   {i}. {place['name']}")
        print(f"      Distance: {place.get('distance_miles', 'N/A')} miles")
        print(f"      Drive time: {place.get('drive_time_minutes', 'N/A')} minutes")
        print(f"      Rating: {place.get('rating', 'N/A')}/5 ({place.get('user_ratings_total', 0)} reviews)")
else:
    print(f"❌ FAIL: {result.get('error')}")
print()

# Test 5: Get Place Details (using first hospital from search)
print("TEST 5: Get Place Details")
print("-" * 60)
if result['status'] == 'success' and result['total_found'] > 0:
    place_id = result['places'][0]['place_id']
    result = get_place_details(place_id)
    if result['status'] == 'success':
        print("✅ PASS")
        print(f"   Name: {result['name']}")
        print(f"   Address: {result['address']}")
        print(f"   Phone: {result.get('phone', 'N/A')}")
        print(f"   Rating: {result.get('rating', 'N/A')}/5")
        if 'opening_hours' in result:
            print(f"   Open now: {result['opening_hours']['open_now']}")
    else:
        print(f"❌ FAIL: {result.get('error')}")
else:
    print("⏭️  SKIP: No place ID from previous test")
print()

# Summary
print("=" * 60)
print("TEST SUITE COMPLETE")
print("=" * 60)
print()
print("Next steps:")
print("1. Review test results above")
print("2. If all tests pass, add MCP to Claude Desktop config")
print("3. See README.md for configuration instructions")
print()
