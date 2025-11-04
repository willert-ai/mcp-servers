"""
Medicare Hospital Compare MCP Server
Provides hospital quality rating data from Medicare.gov

Functions:
- get_hospital_rating: Get overall quality rating for a hospital
- search_hospitals: Search for hospitals by location
- get_hospital_quality_measures: Get detailed quality metrics for a hospital
- compare_hospitals: Compare multiple hospitals side-by-side

API Used: data.medicare.gov (Hospital Compare API)
Free Tier: Yes (no authentication required, publicly available data)
Rate Limits: Reasonable use (500 requests/minute per IP)
"""

from fastmcp import FastMCP
import requests
from typing import Optional, Dict, List, Any
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("medicare-hospital")

# Medicare API base URL
MEDICARE_API_BASE = "https://data.cms.gov/provider-data/api/1"

# API endpoints
HOSPITALS_ENDPOINT = f"{MEDICARE_API_BASE}/datastore/query/xubh-q36u"  # Hospital General Information
QUALITY_ENDPOINT = f"{MEDICARE_API_BASE}/datastore/query/4pq5-n9py"   # Hospital Overall Ratings


@mcp.tool()
def get_hospital_rating(
    hospital_name: str,
    city: str,
    state: str
) -> Dict[str, Any]:
    """
    Get overall quality rating for a hospital (1-5 stars)

    Args:
        hospital_name: Name of the hospital
        city: City where hospital is located
        state: State abbreviation (e.g., 'GA', 'NY')

    Returns:
        Dictionary with hospital rating and quality information

    Example:
        get_hospital_rating("Memorial Health University Medical Center", "Savannah", "GA")
    """
    try:
        # Query Medicare API for hospital ratings
        params = {
            "filter[state][condition][path]": "state",
            "filter[state][condition][operator]": "=",
            "filter[state][condition][value]": state.upper(),
            "filter[city][condition][path]": "city",
            "filter[city][condition][operator]": "=",
            "filter[city][condition][value]": city.upper(),
            "limit": 100
        }

        response = requests.get(QUALITY_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get('results', [])

        # Search for matching hospital
        matches = []
        hospital_name_lower = hospital_name.lower()
        for hospital in results:
            facility_name = hospital.get('facility_name', '').lower()
            if hospital_name_lower in facility_name or facility_name in hospital_name_lower:
                matches.append(hospital)

        if not matches:
            return {
                "status": "not_found",
                "message": f"No hospital found matching '{hospital_name}' in {city}, {state}",
                "searched": {
                    "hospital_name": hospital_name,
                    "city": city,
                    "state": state
                },
                "suggestion": "Try searching by location first to see available hospitals",
                "source": "Medicare Hospital Compare (data.cms.gov)",
                "timestamp": datetime.utcnow().isoformat()
            }

        # Return the best match
        hospital = matches[0]

        return {
            "status": "success",
            "hospital_name": hospital.get('facility_name'),
            "address": hospital.get('address'),
            "city": hospital.get('city'),
            "state": hospital.get('state'),
            "zip_code": hospital.get('zip_code'),
            "phone": hospital.get('phone_number'),
            "hospital_type": hospital.get('hospital_type'),
            "ownership": hospital.get('hospital_ownership'),
            "overall_rating": hospital.get('hospital_overall_rating'),
            "rating_scale": "1-5 stars (5 is best)",
            "rating_footnote": hospital.get('hospital_overall_rating_footnote'),
            "mortality_rating": hospital.get('mortality_national_comparison'),
            "safety_rating": hospital.get('safety_of_care_national_comparison'),
            "readmission_rating": hospital.get('readmission_national_comparison'),
            "patient_experience_rating": hospital.get('patient_experience_national_comparison'),
            "timeliness_rating": hospital.get('timeliness_of_care_national_comparison'),
            "effectiveness_rating": hospital.get('effective_care_national_comparison'),
            "medicare_provider_id": hospital.get('facility_id'),
            "emergency_services": hospital.get('emergency_services'),
            "source": "Medicare Hospital Compare (data.cms.gov)",
            "data_date": hospital.get('measure_end_date'),
            "timestamp": datetime.utcnow().isoformat()
        }

    except requests.RequestException as e:
        return {
            "status": "error",
            "error": f"API request failed: {str(e)}",
            "source": "Medicare Hospital Compare (data.cms.gov)",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def search_hospitals(
    zip_code: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search for hospitals by location

    Args:
        zip_code: ZIP code to search (optional)
        city: City name (optional, requires state if used)
        state: State abbreviation (optional)
        limit: Maximum number of results (default 10, max 50)

    Returns:
        Dictionary with list of hospitals in the area

    Example:
        search_hospitals(zip_code="31419", limit=5)
        search_hospitals(city="Savannah", state="GA", limit=10)
    """
    try:
        if not zip_code and not (city and state):
            return {
                "status": "error",
                "error": "Must provide either zip_code or both city and state"
            }

        # Build query filters
        filters = {}
        filter_count = 0

        if zip_code:
            filters[f"filter[zip][condition][path]"] = "zip_code"
            filters[f"filter[zip][condition][operator]"] = "="
            filters[f"filter[zip][condition][value]"] = zip_code
            filter_count += 1

        if state:
            filters[f"filter[state][condition][path]"] = "state"
            filters[f"filter[state][condition][operator]"] = "="
            filters[f"filter[state][condition][value]"] = state.upper()
            filter_count += 1

        if city:
            filters[f"filter[city][condition][path]"] = "city"
            filters[f"filter[city][condition][operator]"] = "="
            filters[f"filter[city][condition][value]"] = city.upper()
            filter_count += 1

        filters["limit"] = min(limit, 50)

        # Query Medicare API
        response = requests.get(QUALITY_ENDPOINT, params=filters, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get('results', [])

        hospitals = []
        for hospital in results:
            hospitals.append({
                "hospital_name": hospital.get('facility_name'),
                "address": hospital.get('address'),
                "city": hospital.get('city'),
                "state": hospital.get('state'),
                "zip_code": hospital.get('zip_code'),
                "phone": hospital.get('phone_number'),
                "overall_rating": hospital.get('hospital_overall_rating'),
                "hospital_type": hospital.get('hospital_type'),
                "ownership": hospital.get('hospital_ownership'),
                "emergency_services": hospital.get('emergency_services'),
                "medicare_provider_id": hospital.get('facility_id')
            })

        return {
            "status": "success",
            "search_params": {
                "zip_code": zip_code,
                "city": city,
                "state": state
            },
            "total_found": len(hospitals),
            "hospitals": hospitals,
            "source": "Medicare Hospital Compare (data.cms.gov)",
            "timestamp": datetime.utcnow().isoformat()
        }

    except requests.RequestException as e:
        return {
            "status": "error",
            "error": f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_hospital_quality_measures(
    medicare_provider_id: str
) -> Dict[str, Any]:
    """
    Get detailed quality measures for a specific hospital

    Args:
        medicare_provider_id: Medicare Provider ID (6-digit number)

    Returns:
        Dictionary with detailed quality metrics by category

    Example:
        get_hospital_quality_measures("110079")
    """
    try:
        # Query for specific hospital by provider ID
        params = {
            "filter[id][condition][path]": "facility_id",
            "filter[id][condition][operator]": "=",
            "filter[id][condition][value]": medicare_provider_id
        }

        response = requests.get(QUALITY_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get('results', [])

        if not results:
            return {
                "status": "not_found",
                "message": f"No hospital found with Medicare Provider ID: {medicare_provider_id}",
                "source": "Medicare Hospital Compare (data.cms.gov)",
                "timestamp": datetime.utcnow().isoformat()
            }

        hospital = results[0]

        # Organize quality measures by category
        quality_measures = {
            "overall_rating": {
                "rating": hospital.get('hospital_overall_rating'),
                "rating_scale": "1-5 stars",
                "footnote": hospital.get('hospital_overall_rating_footnote')
            },
            "mortality": {
                "national_comparison": hospital.get('mortality_national_comparison'),
                "description": "Death rates for common conditions"
            },
            "safety_of_care": {
                "national_comparison": hospital.get('safety_of_care_national_comparison'),
                "description": "Infections, complications, medical errors"
            },
            "readmission": {
                "national_comparison": hospital.get('readmission_national_comparison'),
                "description": "Rate of patients readmitted within 30 days"
            },
            "patient_experience": {
                "national_comparison": hospital.get('patient_experience_national_comparison'),
                "description": "Patient survey results (HCAHPS)"
            },
            "timeliness_of_care": {
                "national_comparison": hospital.get('timeliness_of_care_national_comparison'),
                "description": "How quickly patients receive care"
            },
            "effective_care": {
                "national_comparison": hospital.get('effective_care_national_comparison'),
                "description": "Following best practices for treatment"
            }
        }

        # Comparison ratings explained
        rating_guide = {
            "Above the national average": "Better than most hospitals",
            "Same as the national average": "Similar to most hospitals",
            "Below the national average": "Worse than most hospitals",
            "Not Available": "Insufficient data"
        }

        return {
            "status": "success",
            "hospital_name": hospital.get('facility_name'),
            "medicare_provider_id": medicare_provider_id,
            "quality_measures": quality_measures,
            "rating_guide": rating_guide,
            "data_date": hospital.get('measure_end_date'),
            "source": "Medicare Hospital Compare (data.cms.gov)",
            "timestamp": datetime.utcnow().isoformat()
        }

    except requests.RequestException as e:
        return {
            "status": "error",
            "error": f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def compare_hospitals(
    hospital_ids: List[str]
) -> Dict[str, Any]:
    """
    Compare multiple hospitals side-by-side

    Args:
        hospital_ids: List of Medicare Provider IDs to compare (max 5)

    Returns:
        Dictionary with comparison table of hospital ratings

    Example:
        compare_hospitals(["110079", "110156"])
    """
    try:
        if len(hospital_ids) > 5:
            return {
                "status": "error",
                "error": "Maximum 5 hospitals can be compared at once"
            }

        comparisons = []
        for provider_id in hospital_ids:
            result = get_hospital_quality_measures(provider_id)
            if result['status'] == 'success':
                comparisons.append({
                    "hospital_name": result['hospital_name'],
                    "medicare_provider_id": provider_id,
                    "overall_rating": result['quality_measures']['overall_rating']['rating'],
                    "mortality": result['quality_measures']['mortality']['national_comparison'],
                    "safety": result['quality_measures']['safety_of_care']['national_comparison'],
                    "readmission": result['quality_measures']['readmission']['national_comparison'],
                    "patient_experience": result['quality_measures']['patient_experience']['national_comparison'],
                    "timeliness": result['quality_measures']['timeliness_of_care']['national_comparison'],
                    "effectiveness": result['quality_measures']['effective_care']['national_comparison']
                })
            else:
                comparisons.append({
                    "hospital_name": "Not Found",
                    "medicare_provider_id": provider_id,
                    "error": "Hospital data not available"
                })

        return {
            "status": "success",
            "total_compared": len(comparisons),
            "hospitals": comparisons,
            "source": "Medicare Hospital Compare (data.cms.gov)",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
