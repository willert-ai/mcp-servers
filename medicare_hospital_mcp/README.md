# Medicare Hospital Compare MCP Server

Model Context Protocol (MCP) server for Medicare Hospital Compare data, providing hospital quality ratings and metrics.

## Purpose

This MCP enables automated retrieval of hospital quality data from Medicare.gov, supporting evidence-based analysis of healthcare proximity for memory care facilities. Part of zero-hallucination research protocol.

## Features

### Available Tools

1. **get_hospital_rating** - Get overall quality rating (1-5 stars) for a specific hospital
2. **search_hospitals** - Find all hospitals in a ZIP code or city
3. **get_hospital_quality_measures** - Get detailed quality metrics by category
4. **compare_hospitals** - Compare multiple hospitals side-by-side

### Data Source

**Medicare Hospital Compare** (data.cms.gov)
- Official CMS (Centers for Medicare & Medicaid Services) data
- Publicly available, no authentication required
- Updated quarterly
- Includes 4,000+ hospitals nationwide

### Quality Metrics Provided

- **Overall Rating**: 1-5 stars
- **Mortality**: Death rates for common conditions
- **Safety of Care**: Infections, complications, medical errors
- **Readmission**: Patients readmitted within 30 days
- **Patient Experience**: HCAHPS survey results
- **Timeliness**: How quickly patients receive care
- **Effectiveness**: Following best practices

Each metric includes national comparison:
- "Above the national average"
- "Same as the national average"
- "Below the national average"

## Setup

### 1. Install Dependencies

```bash
cd "/Users/aiveo/Library/CloudStorage/GoogleDrive-fw@feropartners.com/Meine Ablage/07 LEO/project-management/Savannah/MCPs/medicare-hospital-mcp"
pip install -r requirements.txt
```

### 2. Configure Claude Desktop

Add to your Claude Desktop MCP configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "medicare-hospital": {
      "command": "python",
      "args": [
        "/Users/aiveo/Library/CloudStorage/GoogleDrive-fw@feropartners.com/Meine Ablage/07 LEO/project-management/Savannah/MCPs/medicare-hospital-mcp/server.py"
      ]
    }
  }
}
```

**No API key required** - Medicare data is publicly accessible.

### 3. Restart Claude Desktop

Restart Claude Desktop to load the new MCP server.

## Usage Examples

### Example 1: Search Hospitals by ZIP Code

```python
# Tool: search_hospitals
# Input:
{
  "zip_code": "31419",
  "limit": 5
}

# Output:
{
  "status": "success",
  "search_params": {
    "zip_code": "31419",
    "city": null,
    "state": null
  },
  "total_found": 3,
  "hospitals": [
    {
      "hospital_name": "MEMORIAL HEALTH UNIVERSITY MEDICAL CENTER",
      "address": "4700 WATERS AVENUE",
      "city": "SAVANNAH",
      "state": "GA",
      "zip_code": "31404",
      "phone": "(912) 350-8000",
      "overall_rating": "3",
      "hospital_type": "Acute Care Hospitals",
      "ownership": "Voluntary non-profit - Private",
      "emergency_services": "Yes",
      "medicare_provider_id": "110079"
    },
    {
      "hospital_name": "ST JOSEPHS/CANDLER HOSPITAL",
      "address": "5353 REYNOLDS STREET",
      "city": "SAVANNAH",
      "state": "GA",
      "zip_code": "31405",
      "phone": "(912) 819-6000",
      "overall_rating": "3",
      "hospital_type": "Acute Care Hospitals",
      "ownership": "Voluntary non-profit - Church",
      "emergency_services": "Yes",
      "medicare_provider_id": "110156"
    }
  ],
  "source": "Medicare Hospital Compare (data.cms.gov)",
  "timestamp": "2025-11-03T14:30:00Z"
}
```

### Example 2: Get Hospital Rating by Name

```python
# Tool: get_hospital_rating
# Input:
{
  "hospital_name": "Memorial Health University Medical Center",
  "city": "Savannah",
  "state": "GA"
}

# Output:
{
  "status": "success",
  "hospital_name": "MEMORIAL HEALTH UNIVERSITY MEDICAL CENTER",
  "address": "4700 WATERS AVENUE",
  "city": "SAVANNAH",
  "state": "GA",
  "zip_code": "31404",
  "phone": "(912) 350-8000",
  "hospital_type": "Acute Care Hospitals",
  "ownership": "Voluntary non-profit - Private",
  "overall_rating": "3",
  "rating_scale": "1-5 stars (5 is best)",
  "mortality_rating": "Same as the national average",
  "safety_rating": "Same as the national average",
  "readmission_rating": "Same as the national average",
  "patient_experience_rating": "Same as the national average",
  "timeliness_rating": "Same as the national average",
  "effectiveness_rating": "Above the national average",
  "medicare_provider_id": "110079",
  "emergency_services": "Yes",
  "source": "Medicare Hospital Compare (data.cms.gov)",
  "data_date": "2024-06-30",
  "timestamp": "2025-11-03T14:30:00Z"
}
```

### Example 3: Get Detailed Quality Measures

```python
# Tool: get_hospital_quality_measures
# Input:
{
  "medicare_provider_id": "110079"
}

# Output:
{
  "status": "success",
  "hospital_name": "MEMORIAL HEALTH UNIVERSITY MEDICAL CENTER",
  "medicare_provider_id": "110079",
  "quality_measures": {
    "overall_rating": {
      "rating": "3",
      "rating_scale": "1-5 stars",
      "footnote": null
    },
    "mortality": {
      "national_comparison": "Same as the national average",
      "description": "Death rates for common conditions"
    },
    "safety_of_care": {
      "national_comparison": "Same as the national average",
      "description": "Infections, complications, medical errors"
    },
    "readmission": {
      "national_comparison": "Same as the national average",
      "description": "Rate of patients readmitted within 30 days"
    },
    "patient_experience": {
      "national_comparison": "Same as the national average",
      "description": "Patient survey results (HCAHPS)"
    },
    "timeliness_of_care": {
      "national_comparison": "Same as the national average",
      "description": "How quickly patients receive care"
    },
    "effective_care": {
      "national_comparison": "Above the national average",
      "description": "Following best practices for treatment"
    }
  },
  "rating_guide": {
    "Above the national average": "Better than most hospitals",
    "Same as the national average": "Similar to most hospitals",
    "Below the national average": "Worse than most hospitals",
    "Not Available": "Insufficient data"
  },
  "data_date": "2024-06-30",
  "source": "Medicare Hospital Compare (data.cms.gov)",
  "timestamp": "2025-11-03T14:30:00Z"
}
```

### Example 4: Compare Multiple Hospitals

```python
# Tool: compare_hospitals
# Input:
{
  "hospital_ids": ["110079", "110156"]
}

# Output:
{
  "status": "success",
  "total_compared": 2,
  "hospitals": [
    {
      "hospital_name": "MEMORIAL HEALTH UNIVERSITY MEDICAL CENTER",
      "medicare_provider_id": "110079",
      "overall_rating": "3",
      "mortality": "Same as the national average",
      "safety": "Same as the national average",
      "readmission": "Same as the national average",
      "patient_experience": "Same as the national average",
      "timeliness": "Same as the national average",
      "effectiveness": "Above the national average"
    },
    {
      "hospital_name": "ST JOSEPHS/CANDLER HOSPITAL",
      "medicare_provider_id": "110156",
      "overall_rating": "3",
      "mortality": "Same as the national average",
      "safety": "Same as the national average",
      "readmission": "Same as the national average",
      "patient_experience": "Below the national average",
      "timeliness": "Same as the national average",
      "effectiveness": "Same as the national average"
    }
  ],
  "source": "Medicare Hospital Compare (data.cms.gov)",
  "timestamp": "2025-11-03T14:30:00Z"
}
```

## Integration with Google Maps MCP

For complete location analysis, combine with Google Maps MCP:

```python
# 1. Search hospitals near facility (Medicare MCP)
hospitals = search_hospitals(zip_code="31419", limit=5)

# 2. For each hospital, get distance and drive time (Google Maps MCP)
for hospital in hospitals['hospitals']:
    distance = get_distance(
        "249 Holland Drive, Savannah, GA 31419",
        hospital['address'],
        "driving"
    )

    # 3. Get quality rating (Medicare MCP)
    quality = get_hospital_quality_measures(hospital['medicare_provider_id'])

    # Combined result includes:
    # - Hospital name and contact
    # - Distance and drive time
    # - Quality ratings and comparisons
```

## Understanding Quality Ratings

### Overall Star Rating (1-5 stars)

- **5 stars**: Exceptional quality
- **4 stars**: Above average quality
- **3 stars**: Average quality
- **2 stars**: Below average quality
- **1 star**: Poor quality

### National Comparisons

Medicare compares each hospital to national averages across 6 categories:

1. **Mortality** - How often patients die from serious conditions
2. **Safety** - How well hospitals prevent infections and errors
3. **Readmission** - How often patients return within 30 days
4. **Patient Experience** - What patients say about their care
5. **Timeliness** - How quickly hospitals provide care
6. **Effectiveness** - Following best medical practices

Each category receives one of these comparisons:
- "Above the national average" (better)
- "Same as the national average" (typical)
- "Below the national average" (worse)
- "Not Available" (insufficient data)

## Use Cases for Memory Care Facilities

### Scenario 1: Evaluating Hospital Proximity

When analyzing a memory care facility's location, you can:

1. Search hospitals within 10-mile radius
2. Get distance and drive time for each
3. Check Medicare quality ratings
4. Identify highest-rated hospitals nearest to facility

**Why This Matters:** Memory care residents often have medical emergencies. Families want to know:
- "What hospitals are nearby?"
- "How good are they?"
- "How long does it take to get there?"

### Scenario 2: Comparing Two Facility Locations

When comparing two potential memory care facilities:

1. Find hospitals near each facility
2. Compare ratings of nearby hospitals
3. Assess which facility has better hospital access
4. Include in location analysis report

**Voice Agent Application:** "The nearest hospital is Memorial Health University Medical Center, just 4.2 miles away with a 3-star Medicare rating and above-average effectiveness scores."

## Cost & Usage Limits

### Free Tier
- **100% free** - No API key, no charges, no credit card
- Publicly funded data from CMS

### Rate Limits
- **500 requests per minute per IP** (very generous)
- No daily or monthly limits

### Data Freshness
- Updated **quarterly** by Medicare
- Check `data_date` field in responses for last update

### Typical Usage
- Search hospitals: 1-5 requests per property
- Get ratings: 3-10 requests per property
- Compare hospitals: 1-2 requests per property

**Can analyze:** Unlimited properties (no cost)

## Data Quality Notes

### What Medicare Data Includes

✅ **All Medicare-certified hospitals** (4,000+ nationwide)
✅ **Quality ratings** updated quarterly
✅ **Objective metrics** (mortality, readmissions, infections)
✅ **Patient surveys** (HCAHPS)
✅ **National comparisons**

### What Medicare Data Excludes

❌ **Non-certified facilities** (small clinics, urgent care)
❌ **Veterans Affairs hospitals** (separate system)
❌ **Specialty hospitals** without Medicare certification
❌ **Real-time data** (quarterly updates only)

### For Voice Agent Knowledge Base

When adding hospital information to voice agent KB:

**RECOMMENDED:**
- Mention overall star rating (3 stars, 4 stars, etc.)
- Highlight "above average" categories
- Include distance and drive time
- Name 2-3 closest hospitals

**AVOID:**
- Interpreting ratings without context
- Making medical recommendations
- Claiming quality guarantees
- Comparing quality without data

**Example Voice Agent Response:**
> "The closest hospital is Memorial Health University Medical Center, just over 4 miles away. It has a 3-star Medicare rating, which is average quality, and scores above the national average for effective care. The drive is typically 11-12 minutes."

## Troubleshooting

### "No hospital found" error

**Possible causes:**
- Hospital name spelling doesn't match Medicare records
- Hospital not Medicare-certified
- Hospital in wrong city/state

**Solution:**
1. Use `search_hospitals` first to see exact names
2. Medicare uses ALL CAPS for names
3. Try searching by Medicare Provider ID instead

### API timeout errors

**Possible causes:**
- Medicare API temporarily slow
- Network connectivity issues

**Solution:**
1. Retry after a few seconds
2. Check internet connection
3. Verify data.cms.gov is accessible

### Empty results

**Possible causes:**
- ZIP code has no hospitals nearby
- Search parameters too restrictive

**Solution:**
1. Expand search radius (use nearby ZIP codes)
2. Search by city/state instead of ZIP
3. Check if location is correct

## Related Documentation

- [Research Methodology](../../../Knowledge%20Base/Research_Methodology_Area_Analysis.md)
- [Area Analysis Framework](../../../Knowledge%20Base/Framework_Area_Analysis_Memory_Care.md)
- [Google Maps MCP](../google-maps-mcp/README.md) - For distance/drive time data

## Official Resources

- [Medicare Hospital Compare Website](https://www.medicare.gov/care-compare/)
- [CMS Data API Documentation](https://data.cms.gov/provider-data/)
- [Hospital Quality Star Ratings](https://www.cms.gov/medicare/quality/initiatives/hospital-quality-initiative/overall-hospital-quality-star-ratings)

## License

Internal tool for LEO project. Not for public distribution.

## Support

For issues or questions, contact Florian (LEO Voice Agent Pilot).

---

**Created:** November 3, 2025
**Version:** 1.0.0
**Purpose:** Hospital quality ratings for memory care facility location analysis (zero-hallucination protocol)
