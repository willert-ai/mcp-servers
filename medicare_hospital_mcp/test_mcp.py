"""
Test script for Medicare Hospital Compare MCP

This script tests all MCP functions to verify they work correctly
before integrating with Claude Desktop.

Setup:
1. Install dependencies: pip install -r requirements.txt
2. Run: python test_mcp.py

No API key required - Medicare data is publicly accessible.
"""

# Import server functions
from server import (
    get_hospital_rating,
    search_hospitals,
    get_hospital_quality_measures,
    compare_hospitals
)

print("=" * 60)
print("MEDICARE HOSPITAL COMPARE MCP TEST SUITE")
print("=" * 60)
print()
print("NOTE: No API key required - Medicare data is public")
print()

# Test location
TEST_CITY = "Savannah"
TEST_STATE = "GA"
TEST_ZIP = "31419"

# Test 1: Search Hospitals by ZIP
print("TEST 1: Search Hospitals by ZIP Code")
print("-" * 60)
result = search_hospitals(zip_code=TEST_ZIP, limit=5)
if result['status'] == 'success':
    print("✅ PASS")
    print(f"   Found: {result['total_found']} hospitals near ZIP {TEST_ZIP}")
    hospitals = result['hospitals']
    for i, hospital in enumerate(hospitals[:3], 1):
        print(f"   {i}. {hospital['hospital_name']}")
        print(f"      Address: {hospital['address']}, {hospital['city']}")
        print(f"      Rating: {hospital.get('overall_rating', 'N/A')}/5 stars")
        print(f"      Medicare ID: {hospital['medicare_provider_id']}")
        print(f"      Emergency Services: {hospital.get('emergency_services', 'N/A')}")
else:
    print(f"❌ FAIL: {result.get('error')}")
    hospitals = []
print()

# Test 2: Search Hospitals by City/State
print("TEST 2: Search Hospitals by City and State")
print("-" * 60)
result = search_hospitals(city=TEST_CITY, state=TEST_STATE, limit=5)
if result['status'] == 'success':
    print("✅ PASS")
    print(f"   Found: {result['total_found']} hospitals in {TEST_CITY}, {TEST_STATE}")
else:
    print(f"❌ FAIL: {result.get('error')}")
print()

# Test 3: Get Hospital Rating by Name
print("TEST 3: Get Hospital Rating by Name")
print("-" * 60)
if hospitals:
    test_hospital_name = hospitals[0]['hospital_name']
    result = get_hospital_rating(test_hospital_name, TEST_CITY, TEST_STATE)
    if result['status'] == 'success':
        print("✅ PASS")
        print(f"   Hospital: {result['hospital_name']}")
        print(f"   Overall Rating: {result.get('overall_rating', 'N/A')}/5 stars")
        print(f"   Phone: {result.get('phone', 'N/A')}")
        print(f"   Type: {result.get('hospital_type', 'N/A')}")
        print(f"   Ownership: {result.get('ownership', 'N/A')}")
        print()
        print("   Quality Comparisons to National Average:")
        print(f"   - Mortality: {result.get('mortality_rating', 'N/A')}")
        print(f"   - Safety: {result.get('safety_rating', 'N/A')}")
        print(f"   - Readmission: {result.get('readmission_rating', 'N/A')}")
        print(f"   - Patient Experience: {result.get('patient_experience_rating', 'N/A')}")
        print(f"   - Timeliness: {result.get('timeliness_rating', 'N/A')}")
        print(f"   - Effectiveness: {result.get('effectiveness_rating', 'N/A')}")
        print()
        print(f"   Data Date: {result.get('data_date', 'N/A')}")
    else:
        print(f"❌ FAIL: {result.get('error')}")
        print(f"   Message: {result.get('message', 'Unknown error')}")
else:
    print("⏭️  SKIP: No hospitals from previous test")
print()

# Test 4: Get Detailed Quality Measures
print("TEST 4: Get Detailed Quality Measures")
print("-" * 60)
if hospitals:
    provider_id = hospitals[0]['medicare_provider_id']
    result = get_hospital_quality_measures(provider_id)
    if result['status'] == 'success':
        print("✅ PASS")
        print(f"   Hospital: {result['hospital_name']}")
        print(f"   Medicare Provider ID: {result['medicare_provider_id']}")
        print()
        print("   Quality Measures:")
        measures = result['quality_measures']
        for category, data in measures.items():
            if category != 'overall_rating':
                print(f"   - {category.replace('_', ' ').title()}:")
                print(f"     Comparison: {data.get('national_comparison', 'N/A')}")
                print(f"     ({data.get('description', '')})")
    else:
        print(f"❌ FAIL: {result.get('error')}")
else:
    print("⏭️  SKIP: No hospitals from previous test")
print()

# Test 5: Compare Multiple Hospitals
print("TEST 5: Compare Multiple Hospitals")
print("-" * 60)
if len(hospitals) >= 2:
    ids_to_compare = [h['medicare_provider_id'] for h in hospitals[:2]]
    result = compare_hospitals(ids_to_compare)
    if result['status'] == 'success':
        print("✅ PASS")
        print(f"   Comparing {result['total_compared']} hospitals:")
        print()
        for hospital in result['hospitals']:
            if 'error' not in hospital:
                print(f"   {hospital['hospital_name']}")
                print(f"   - Overall Rating: {hospital.get('overall_rating', 'N/A')}/5 stars")
                print(f"   - Mortality: {hospital.get('mortality', 'N/A')}")
                print(f"   - Safety: {hospital.get('safety', 'N/A')}")
                print(f"   - Patient Experience: {hospital.get('patient_experience', 'N/A')}")
                print()
    else:
        print(f"❌ FAIL: {result.get('error')}")
elif len(hospitals) == 1:
    print("⏭️  SKIP: Need at least 2 hospitals to compare")
else:
    print("⏭️  SKIP: No hospitals from previous test")
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
print("4. Combine with Google Maps MCP for complete location analysis")
print()
print("Note: Medicare data is updated quarterly by CMS")
print("Rating scale: 1-5 stars (5 is best)")
print()
