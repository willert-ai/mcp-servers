#!/usr/bin/env python3
'''
Google Places MCP Server for Property Research

This server provides comprehensive tools to interact with Google Maps Platform APIs,
specifically designed for researching properties and their surrounding areas. It integrates:
- Places API (New) for finding and analyzing nearby amenities
- Routes API for distance and drive time calculations
- Geocoding API for address validation and coordinate conversion
'''

import os
import json
from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("google_places_mcp")

# Constants
CHARACTER_LIMIT = 25000  # Maximum response size in characters
PLACES_API_BASE_URL = "https://places.googleapis.com/v1"
ROUTES_API_BASE_URL = "https://routes.googleapis.com"
GEOCODING_API_BASE_URL = "https://maps.googleapis.com/maps/api/geocode"

# Get API key from environment
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Enums
class ResponseFormat(str, Enum):
    '''Output format for tool responses.'''
    MARKDOWN = "markdown"
    JSON = "json"

class PlaceType(str, Enum):
    '''Common place types for nearby search.'''
    HOSPITAL = "hospital"
    HOTEL = "hotel"
    LODGING = "lodging"
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    PARK = "park"
    CHURCH = "church"
    SYNAGOGUE = "synagogue"
    MOSQUE = "mosque"
    AIRPORT = "airport"
    GAS_STATION = "gas_station"
    PHARMACY = "pharmacy"
    SHOPPING_MALL = "shopping_mall"
    BANK = "bank"
    ATM = "atm"
    TOURIST_ATTRACTION = "tourist_attraction"

class TravelMode(str, Enum):
    '''Travel modes for route calculations.'''
    DRIVE = "DRIVE"
    WALK = "WALK"
    BICYCLE = "BICYCLE"
    TRANSIT = "TRANSIT"
    TWO_WHEELER = "TWO_WHEELER"

# Pydantic Models for Input Validation

class NearbySearchInput(BaseModel):
    '''Input model for nearby place search.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    location: str = Field(
        ...,
        description="Address or location to search near (e.g., '249 Holland Drive, Savannah, GA 31419' or '32.0809,-81.0912')",
        min_length=3,
        max_length=500
    )
    place_types: List[str] = Field(
        ...,
        description="List of place types to search for (e.g., ['hospital', 'hotel', 'restaurant']). Available types: hospital, hotel, lodging, restaurant, cafe, park, church, synagogue, mosque, airport, gas_station, pharmacy, shopping_mall, bank, atm, tourist_attraction",
        min_length=1,
        max_length=10
    )
    radius_miles: Optional[float] = Field(
        default=10.0,
        description="Search radius in miles (default: 10.0)",
        ge=0.1,
        le=50.0
    )
    max_results: Optional[int] = Field(
        default=20,
        description="Maximum number of results per place type (default: 20, max: 20)",
        ge=1,
        le=20
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )

class TextSearchInput(BaseModel):
    '''Input model for text-based place search.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    query: str = Field(
        ...,
        description="Search query text (e.g., 'Memorial Health University Medical Center Savannah', 'pizza restaurants near me')",
        min_length=2,
        max_length=500
    )
    location_bias: Optional[str] = Field(
        default=None,
        description="Optional address or coordinates to bias results toward (e.g., '249 Holland Drive, Savannah, GA' or '32.0809,-81.0912')",
        max_length=500
    )
    max_results: Optional[int] = Field(
        default=10,
        description="Maximum number of results (default: 10, max: 20)",
        ge=1,
        le=20
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

class PlaceDetailsInput(BaseModel):
    '''Input model for getting place details.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    place_id: str = Field(
        ...,
        description="Google Place ID (obtained from search results, e.g., 'ChIJN1t_tDeuEmsRUsoyG83frY4')",
        min_length=10,
        max_length=200
    )
    include_reviews: Optional[bool] = Field(
        default=True,
        description="Include user reviews in response (default: True)"
    )
    max_reviews: Optional[int] = Field(
        default=5,
        description="Maximum number of reviews to include (default: 5)",
        ge=1,
        le=20
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

class ComputeRouteInput(BaseModel):
    '''Input model for computing routes and travel times.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    origin: str = Field(
        ...,
        description="Starting address or coordinates (e.g., '249 Holland Drive, Savannah, GA 31419' or '32.0809,-81.0912')",
        min_length=3,
        max_length=500
    )
    destination: str = Field(
        ...,
        description="Destination address or coordinates (e.g., 'Savannah/Hilton Head International Airport' or '32.1276,-81.2021')",
        min_length=3,
        max_length=500
    )
    travel_mode: TravelMode = Field(
        default=TravelMode.DRIVE,
        description="Mode of transportation: DRIVE, WALK, BICYCLE, TRANSIT, TWO_WHEELER (default: DRIVE)"
    )
    departure_time: Optional[str] = Field(
        default=None,
        description="Optional departure time in ISO 8601 format (e.g., '2025-11-03T14:30:00-05:00') for traffic-aware routing. If not specified, uses current time.",
        max_length=100
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

class DistanceMatrixInput(BaseModel):
    '''Input model for computing distance matrix.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    origins: List[str] = Field(
        ...,
        description="List of starting addresses or coordinates (max 25)",
        min_length=1,
        max_length=25
    )
    destinations: List[str] = Field(
        ...,
        description="List of destination addresses or coordinates (max 25)",
        min_length=1,
        max_length=25
    )
    travel_mode: TravelMode = Field(
        default=TravelMode.DRIVE,
        description="Mode of transportation: DRIVE, WALK, BICYCLE, TRANSIT (default: DRIVE)"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

class GeocodeInput(BaseModel):
    '''Input model for geocoding addresses.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    address: str = Field(
        ...,
        description="Address to geocode (e.g., '249 Holland Drive, Savannah, GA 31419')",
        min_length=3,
        max_length=500
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

class ReverseGeocodeInput(BaseModel):
    '''Input model for reverse geocoding coordinates.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    latitude: float = Field(
        ...,
        description="Latitude coordinate (e.g., 32.0809)",
        ge=-90.0,
        le=90.0
    )
    longitude: float = Field(
        ...,
        description="Longitude coordinate (e.g., -81.0912)",
        ge=-180.0,
        le=180.0
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

# Shared utility functions

def _check_api_key() -> bool:
    '''Check if API key is configured.'''
    return bool(API_KEY and API_KEY != "")

def _handle_api_error(e: Exception) -> str:
    '''Consistent error formatting across all tools.'''
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 400:
            try:
                error_data = e.response.json()
                error_message = error_data.get('error', {}).get('message', 'Bad request')
                return f"Error: Invalid request - {error_message}. Please check your parameters."
            except:
                return "Error: Invalid request. Please check your parameters."
        elif e.response.status_code == 401:
            return "Error: Invalid API key. Please verify your GOOGLE_MAPS_API_KEY environment variable."
        elif e.response.status_code == 403:
            return "Error: API access forbidden. Ensure the API is enabled in your Google Cloud Console and the key has proper permissions."
        elif e.response.status_code == 404:
            return "Error: Resource not found. Please check the place ID or address is correct."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    elif isinstance(e, httpx.ConnectError):
        return "Error: Could not connect to Google Maps API. Please check your internet connection."
    return f"Error: Unexpected error occurred: {type(e).__name__} - {str(e)}"

async def _geocode_location(location: str) -> Optional[Dict[str, float]]:
    '''Helper function to geocode a location string to coordinates.'''
    # Check if already coordinates
    if ',' in location:
        try:
            parts = location.split(',')
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lng = float(parts[1].strip())
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    return {"latitude": lat, "longitude": lng}
        except ValueError:
            pass

    # Geocode the address
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GEOCODING_API_BASE_URL}/json",
            params={"address": location, "key": API_KEY},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "OK" and data.get("results"):
            coords = data["results"][0]["geometry"]["location"]
            return {"latitude": coords["lat"], "longitude": coords["lng"]}

    return None

def _meters_to_miles(meters: float) -> float:
    '''Convert meters to miles.'''
    return meters * 0.000621371

def _format_duration(seconds: int) -> str:
    '''Format duration in seconds to human-readable format.'''
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"

# Tool implementations

@mcp.tool(
    name="google_places_nearby_search",
    annotations={
        "title": "Search for Nearby Places",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def google_places_nearby_search(params: NearbySearchInput) -> str:
    '''
    Search for places near a specific location by type (hospitals, hotels, restaurants, etc.).

    This tool finds businesses and points of interest within a specified radius of a location,
    filtered by place type. It returns essential information including name, address, rating,
    and distance from the search center. Ideal for area analysis and finding amenities near
    a property.

    Args:
        params (NearbySearchInput): Validated input parameters containing:
            - location (str): Address or coordinates to search near (e.g., '249 Holland Drive, Savannah, GA')
            - place_types (List[str]): Place types to find (e.g., ['hospital', 'hotel', 'restaurant'])
            - radius_miles (Optional[float]): Search radius in miles (default: 10.0, max: 50.0)
            - max_results (Optional[int]): Results per place type (default: 20, max: 20)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Formatted results containing:

        Success response (markdown):
            # Nearby Places: [location]
            Search radius: X miles

            ## [Place Type] (X results)

            ### [Place Name] ⭐ X.X
            - **Address**: [full address]
            - **Distance**: X.X miles
            - **Phone**: [if available]
            - **Status**: Open/Closed
            - **Place ID**: [for getting more details]

        Success response (json):
            {
                "search_location": str,
                "radius_miles": float,
                "results_by_type": {
                    "[place_type]": [
                        {
                            "name": str,
                            "address": str,
                            "rating": float,
                            "user_ratings_total": int,
                            "distance_miles": float,
                            "place_id": str,
                            "phone": str,
                            "open_now": bool
                        }
                    ]
                },
                "total_results": int
            }

        Error response:
            "Error: [error message]"

    Examples:
        - Use when: "Find all hospitals within 10 miles of the property"
        - Use when: "Search for hotels and restaurants near the facility"
        - Use when: "Locate churches and parks in the area"
        - Don't use when: You need detailed reviews (use google_places_get_details)
        - Don't use when: Searching by text query (use google_places_text_search)

    Error Handling:
        - Returns "Error: API key not configured" if GOOGLE_MAPS_API_KEY not set
        - Returns "Error: Could not geocode location" if address is invalid
        - Returns "Error: Rate limit exceeded" if too many requests (429 status)
        - Returns formatted results or "No places found" message
    '''
    if not _check_api_key():
        return "Error: Google Maps API key not configured. Please set the GOOGLE_MAPS_API_KEY environment variable."

    try:
        # Geocode the location
        coords = await _geocode_location(params.location)
        if not coords:
            return f"Error: Could not geocode location '{params.location}'. Please provide a valid address or coordinates."

        radius_meters = params.radius_miles * 1609.34  # Convert miles to meters

        results_by_type = {}
        total_count = 0

        # Search for each place type
        for place_type in params.place_types:
            async with httpx.AsyncClient() as client:
                request_body = {
                    "includedTypes": [place_type],
                    "maxResultCount": params.max_results,
                    "locationRestriction": {
                        "circle": {
                            "center": {
                                "latitude": coords["latitude"],
                                "longitude": coords["longitude"]
                            },
                            "radius": radius_meters
                        }
                    }
                }

                response = await client.post(
                    f"{PLACES_API_BASE_URL}/places:searchNearby",
                    headers={
                        "Content-Type": "application/json",
                        "X-Goog-Api-Key": API_KEY,
                        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.location,places.id,places.nationalPhoneNumber,places.currentOpeningHours"
                    },
                    json=request_body,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                places = data.get("places", [])
                results_by_type[place_type] = []

                for place in places:
                    place_lat = place.get("location", {}).get("latitude", 0)
                    place_lng = place.get("location", {}).get("longitude", 0)

                    # Calculate distance using Haversine formula approximation
                    import math
                    lat1, lon1 = math.radians(coords["latitude"]), math.radians(coords["longitude"])
                    lat2, lon2 = math.radians(place_lat), math.radians(place_lng)
                    dlat, dlon = lat2 - lat1, lon2 - lon1
                    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                    c = 2 * math.asin(math.sqrt(a))
                    distance_miles = 3959 * c  # Earth radius in miles

                    place_data = {
                        "name": place.get("displayName", {}).get("text", "Unknown"),
                        "address": place.get("formattedAddress", "N/A"),
                        "rating": place.get("rating"),
                        "user_ratings_total": place.get("userRatingCount", 0),
                        "distance_miles": round(distance_miles, 2),
                        "place_id": place.get("id", "").replace("places/", ""),
                        "phone": place.get("nationalPhoneNumber"),
                        "open_now": place.get("currentOpeningHours", {}).get("openNow")
                    }
                    results_by_type[place_type].append(place_data)
                    total_count += 1

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [
                f"# Nearby Places: {params.location}",
                f"Search radius: {params.radius_miles} miles",
                f"Total results: {total_count}",
                ""
            ]

            for place_type, places in results_by_type.items():
                if places:
                    lines.append(f"## {place_type.replace('_', ' ').title()} ({len(places)} results)")
                    lines.append("")

                    for place in places:
                        rating_str = f"⭐ {place['rating']}" if place['rating'] else "No rating"
                        lines.append(f"### {place['name']} {rating_str}")
                        lines.append(f"- **Address**: {place['address']}")
                        lines.append(f"- **Distance**: {place['distance_miles']} miles")
                        if place['phone']:
                            lines.append(f"- **Phone**: {place['phone']}")
                        if place['open_now'] is not None:
                            status = "Open now" if place['open_now'] else "Closed"
                            lines.append(f"- **Status**: {status}")
                        if place['user_ratings_total']:
                            lines.append(f"- **Reviews**: {place['user_ratings_total']} ratings")
                        lines.append(f"- **Place ID**: {place['place_id']}")
                        lines.append("")
                else:
                    lines.append(f"## {place_type.replace('_', ' ').title()} (0 results)")
                    lines.append("No places found of this type.")
                    lines.append("")

            result = "\n".join(lines)
        else:
            result = json.dumps({
                "search_location": params.location,
                "search_coordinates": coords,
                "radius_miles": params.radius_miles,
                "results_by_type": results_by_type,
                "total_results": total_count
            }, indent=2)

        # Check character limit
        if len(result) > CHARACTER_LIMIT:
            truncation_note = f"\n\n[Response truncated - exceeded {CHARACTER_LIMIT} character limit. Try reducing radius_miles or max_results.]"
            result = result[:CHARACTER_LIMIT - len(truncation_note)] + truncation_note

        return result

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="google_places_text_search",
    annotations={
        "title": "Search Places by Text Query",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def google_places_text_search(params: TextSearchInput) -> str:
    '''
    Search for places using a text query (e.g., "Memorial Health Hospital Savannah").

    This tool performs text-based searches for places, supporting queries like business names,
    categories with locations, or descriptive searches. Results can be biased toward a specific
    location for more relevant results.

    Args:
        params (TextSearchInput): Validated input parameters containing:
            - query (str): Search text (e.g., 'Memorial Health Hospital Savannah')
            - location_bias (Optional[str]): Address or coordinates to bias results toward
            - max_results (Optional[int]): Maximum results (default: 10, max: 20)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Formatted search results with place details

        Success response (markdown):
            # Search Results: "[query]"
            Found X results

            ## [Place Name] ⭐ X.X
            - **Address**: [full address]
            - **Type**: [primary type]
            - **Phone**: [if available]
            - **Website**: [if available]
            - **Place ID**: [for getting more details]

        Success response (json):
            {
                "query": str,
                "results": [
                    {
                        "name": str,
                        "address": str,
                        "rating": float,
                        "user_ratings_total": int,
                        "place_id": str,
                        "types": List[str],
                        "phone": str,
                        "website": str,
                        "coordinates": {"latitude": float, "longitude": float}
                    }
                ],
                "total_results": int
            }

        Error response:
            "Error: [error message]"

    Examples:
        - Use when: "Find Memorial Health University Medical Center in Savannah"
        - Use when: "Search for Savannah/Hilton Head International Airport"
        - Use when: "Look up Forsyth Park Savannah"
        - Don't use when: You want all places of a type in an area (use nearby_search)
        - Don't use when: You already have the place ID (use get_details)

    Error Handling:
        - Returns "Error: API key not configured" if GOOGLE_MAPS_API_KEY not set
        - Returns "No results found" if query matches no places
        - Returns formatted results or error message
    '''
    if not _check_api_key():
        return "Error: Google Maps API key not configured. Please set the GOOGLE_MAPS_API_KEY environment variable."

    try:
        request_body = {
            "textQuery": params.query,
            "maxResultCount": params.max_results
        }

        # Add location bias if provided
        if params.location_bias:
            coords = await _geocode_location(params.location_bias)
            if coords:
                request_body["locationBias"] = {
                    "circle": {
                        "center": {
                            "latitude": coords["latitude"],
                            "longitude": coords["longitude"]
                        },
                        "radius": 50000  # 50km bias radius
                    }
                }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PLACES_API_BASE_URL}/places:searchText",
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": API_KEY,
                    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.id,places.types,places.nationalPhoneNumber,places.websiteUri,places.location"
                },
                json=request_body,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        places = data.get("places", [])

        if not places:
            return f"No results found for query: '{params.query}'"

        results = []
        for place in places:
            place_data = {
                "name": place.get("displayName", {}).get("text", "Unknown"),
                "address": place.get("formattedAddress", "N/A"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("userRatingCount", 0),
                "place_id": place.get("id", "").replace("places/", ""),
                "types": place.get("types", []),
                "phone": place.get("nationalPhoneNumber"),
                "website": place.get("websiteUri"),
                "coordinates": {
                    "latitude": place.get("location", {}).get("latitude"),
                    "longitude": place.get("location", {}).get("longitude")
                }
            }
            results.append(place_data)

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [
                f"# Search Results: \"{params.query}\"",
                f"Found {len(results)} results",
                ""
            ]

            for place in results:
                rating_str = f"⭐ {place['rating']}" if place['rating'] else "No rating"
                lines.append(f"## {place['name']} {rating_str}")
                lines.append(f"- **Address**: {place['address']}")
                if place['types']:
                    primary_type = place['types'][0].replace('_', ' ').title()
                    lines.append(f"- **Type**: {primary_type}")
                if place['phone']:
                    lines.append(f"- **Phone**: {place['phone']}")
                if place['website']:
                    lines.append(f"- **Website**: {place['website']}")
                if place['user_ratings_total']:
                    lines.append(f"- **Reviews**: {place['user_ratings_total']} ratings")
                if place['coordinates']['latitude']:
                    lines.append(f"- **Coordinates**: {place['coordinates']['latitude']}, {place['coordinates']['longitude']}")
                lines.append(f"- **Place ID**: {place['place_id']}")
                lines.append("")

            result = "\n".join(lines)
        else:
            result = json.dumps({
                "query": params.query,
                "results": results,
                "total_results": len(results)
            }, indent=2)

        # Check character limit
        if len(result) > CHARACTER_LIMIT:
            truncation_note = f"\n\n[Response truncated - exceeded {CHARACTER_LIMIT} character limit. Try reducing max_results.]"
            result = result[:CHARACTER_LIMIT - len(truncation_note)] + truncation_note

        return result

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="google_places_get_details",
    annotations={
        "title": "Get Detailed Place Information",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def google_places_get_details(params: PlaceDetailsInput) -> str:
    '''
    Get comprehensive details about a specific place using its Place ID.

    This tool retrieves complete information about a place including contact details, hours,
    ratings, reviews, photos, accessibility features, and amenities. Use this after getting
    a Place ID from search results to get the full picture.

    Args:
        params (PlaceDetailsInput): Validated input parameters containing:
            - place_id (str): Google Place ID from search results
            - include_reviews (Optional[bool]): Include user reviews (default: True)
            - max_reviews (Optional[int]): Max reviews to include (default: 5, max: 20)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Comprehensive place information

        Success response (markdown):
            # [Place Name]
            ⭐ X.X rating (X reviews)

            ## Basic Information
            - **Address**: [full address]
            - **Phone**: [phone number]
            - **Website**: [website URL]
            - **Type**: [primary type]

            ## Hours
            [Operating hours for each day]

            ## Reviews
            ### ⭐ X.X - [Author] ([relative time])
            [Review text]

            ## Additional Details
            - Accessibility, parking, amenities, etc.

        Error response:
            "Error: [error message]"

    Examples:
        - Use when: "Get full details about Memorial Health Hospital"
        - Use when: "What are the hours and reviews for this hotel?"
        - Use when: "Tell me everything about this place" (with Place ID)
        - Don't use when: You don't have a Place ID (search first)

    Error Handling:
        - Returns "Error: API key not configured" if GOOGLE_MAPS_API_KEY not set
        - Returns "Error: Place not found" if Place ID is invalid
        - Returns formatted details or error message
    '''
    if not _check_api_key():
        return "Error: Google Maps API key not configured. Please set the GOOGLE_MAPS_API_KEY environment variable."

    try:
        # Build field mask for comprehensive details
        field_mask_parts = [
            "displayName",
            "formattedAddress",
            "rating",
            "userRatingCount",
            "nationalPhoneNumber",
            "internationalPhoneNumber",
            "websiteUri",
            "googleMapsUri",
            "types",
            "location",
            "viewport",
            "currentOpeningHours",
            "priceLevel",
            "takeout",
            "delivery",
            "dineIn",
            "servesBreakfast",
            "servesLunch",
            "servesDinner",
            "servesBeer",
            "servesWine",
            "servesVegetarianFood",
            "wheelchairAccessibleEntrance",
            "wheelchairAccessibleParking",
            "wheelchairAccessibleRestroom",
            "wheelchairAccessibleSeating",
            "parkingOptions",
            "paymentOptions",
            "goodForChildren",
            "goodForGroups",
            "allowsDogs"
        ]

        if params.include_reviews:
            field_mask_parts.append("reviews")

        field_mask = ",".join(field_mask_parts)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PLACES_API_BASE_URL}/places/{params.place_id}",
                headers={
                    "X-Goog-Api-Key": API_KEY,
                    "X-Goog-FieldMask": field_mask
                },
                timeout=30.0
            )
            response.raise_for_status()
            place = response.json()

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = []

            # Header
            name = place.get("displayName", {}).get("text", "Unknown Place")
            rating = place.get("rating")
            review_count = place.get("userRatingCount", 0)

            lines.append(f"# {name}")
            if rating:
                lines.append(f"⭐ {rating} rating ({review_count:,} reviews)")
            lines.append("")

            # Basic Information
            lines.append("## Basic Information")
            lines.append(f"- **Address**: {place.get('formattedAddress', 'N/A')}")

            if place.get("nationalPhoneNumber"):
                lines.append(f"- **Phone**: {place['nationalPhoneNumber']}")
            if place.get("websiteUri"):
                lines.append(f"- **Website**: {place['websiteUri']}")
            if place.get("googleMapsUri"):
                lines.append(f"- **Google Maps**: {place['googleMapsUri']}")

            types = place.get("types", [])
            if types:
                primary_type = types[0].replace('_', ' ').title()
                lines.append(f"- **Type**: {primary_type}")

            price_level = place.get("priceLevel")
            if price_level:
                lines.append(f"- **Price Level**: {'$' * price_level}")

            coords = place.get("location", {})
            if coords.get("latitude"):
                lines.append(f"- **Coordinates**: {coords['latitude']}, {coords['longitude']}")

            lines.append("")

            # Opening Hours
            hours = place.get("currentOpeningHours", {})
            if hours:
                lines.append("## Hours")
                weekday_texts = hours.get("weekdayDescriptions", [])
                for day_hours in weekday_texts:
                    lines.append(f"- {day_hours}")
                lines.append("")

            # Features & Amenities
            features = []
            if place.get("takeout"): features.append("Takeout")
            if place.get("delivery"): features.append("Delivery")
            if place.get("dineIn"): features.append("Dine-in")
            if place.get("servesBreakfast"): features.append("Breakfast")
            if place.get("servesLunch"): features.append("Lunch")
            if place.get("servesDinner"): features.append("Dinner")
            if place.get("servesBeer"): features.append("Beer")
            if place.get("servesWine"): features.append("Wine")
            if place.get("servesVegetarianFood"): features.append("Vegetarian options")
            if place.get("goodForChildren"): features.append("Good for children")
            if place.get("goodForGroups"): features.append("Good for groups")
            if place.get("allowsDogs"): features.append("Dogs allowed")

            if features:
                lines.append("## Features & Amenities")
                lines.append(f"- {', '.join(features)}")
                lines.append("")

            # Accessibility
            accessibility = []
            if place.get("wheelchairAccessibleEntrance"): accessibility.append("Wheelchair accessible entrance")
            if place.get("wheelchairAccessibleParking"): accessibility.append("Wheelchair accessible parking")
            if place.get("wheelchairAccessibleRestroom"): accessibility.append("Wheelchair accessible restroom")
            if place.get("wheelchairAccessibleSeating"): accessibility.append("Wheelchair accessible seating")

            if accessibility:
                lines.append("## Accessibility")
                for item in accessibility:
                    lines.append(f"- {item}")
                lines.append("")

            # Parking & Payment
            parking = place.get("parkingOptions", {})
            payment = place.get("paymentOptions", {})

            if parking or payment:
                lines.append("## Parking & Payment")
                if parking.get("freeParking"): lines.append("- Free parking available")
                if parking.get("paidParkingLot"): lines.append("- Paid parking lot")
                if parking.get("paidStreetParking"): lines.append("- Paid street parking")
                if parking.get("valetParking"): lines.append("- Valet parking")

                if payment.get("creditCards"): lines.append("- Accepts credit cards")
                if payment.get("debitCards"): lines.append("- Accepts debit cards")
                if payment.get("cash"): lines.append("- Accepts cash")
                if payment.get("nfc"): lines.append("- Accepts NFC payments")
                lines.append("")

            # Reviews
            if params.include_reviews:
                reviews = place.get("reviews", [])
                if reviews:
                    lines.append(f"## Recent Reviews (showing {min(len(reviews), params.max_reviews)} of {review_count:,})")
                    lines.append("")

                    for review in reviews[:params.max_reviews]:
                        author = review.get("authorAttribution", {}).get("displayName", "Anonymous")
                        rating_val = review.get("rating", 0)
                        rel_time = review.get("relativePublishTimeDescription", "")
                        text = review.get("text", {}).get("text", "")

                        lines.append(f"### ⭐ {rating_val} - {author} ({rel_time})")
                        if text:
                            # Truncate long reviews
                            if len(text) > 500:
                                text = text[:500] + "..."
                            lines.append(text)
                        lines.append("")

            result = "\n".join(lines)
        else:
            # JSON format - return structured data
            result_data = {
                "name": place.get("displayName", {}).get("text"),
                "address": place.get("formattedAddress"),
                "phone": place.get("nationalPhoneNumber"),
                "website": place.get("websiteUri"),
                "google_maps_url": place.get("googleMapsUri"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("userRatingCount"),
                "types": place.get("types"),
                "price_level": place.get("priceLevel"),
                "coordinates": place.get("location"),
                "opening_hours": place.get("currentOpeningHours"),
                "features": {
                    "takeout": place.get("takeout"),
                    "delivery": place.get("delivery"),
                    "dine_in": place.get("dineIn"),
                    "good_for_children": place.get("goodForChildren"),
                    "good_for_groups": place.get("goodForGroups"),
                    "allows_dogs": place.get("allowsDogs")
                },
                "accessibility": {
                    "wheelchair_accessible_entrance": place.get("wheelchairAccessibleEntrance"),
                    "wheelchair_accessible_parking": place.get("wheelchairAccessibleParking"),
                    "wheelchair_accessible_restroom": place.get("wheelchairAccessibleRestroom"),
                    "wheelchair_accessible_seating": place.get("wheelchairAccessibleSeating")
                },
                "parking_options": place.get("parkingOptions"),
                "payment_options": place.get("paymentOptions")
            }

            if params.include_reviews:
                reviews = place.get("reviews", [])
                result_data["reviews"] = [
                    {
                        "author": r.get("authorAttribution", {}).get("displayName"),
                        "rating": r.get("rating"),
                        "text": r.get("text", {}).get("text"),
                        "relative_time": r.get("relativePublishTimeDescription")
                    }
                    for r in reviews[:params.max_reviews]
                ]

            result = json.dumps(result_data, indent=2)

        # Check character limit
        if len(result) > CHARACTER_LIMIT:
            truncation_note = f"\n\n[Response truncated - exceeded {CHARACTER_LIMIT} character limit. Try setting include_reviews=False or reducing max_reviews.]"
            result = result[:CHARACTER_LIMIT - len(truncation_note)] + truncation_note

        return result

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="google_routes_compute_route",
    annotations={
        "title": "Calculate Route, Distance & Drive Time",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def google_routes_compute_route(params: ComputeRouteInput) -> str:
    '''
    Calculate the route, distance, and travel time between two locations.

    This tool uses Google's Routes API to compute optimal routes with real-time traffic data,
    providing accurate distance and duration estimates. Supports multiple travel modes and
    can account for traffic conditions at specific departure times.

    Args:
        params (ComputeRouteInput): Validated input parameters containing:
            - origin (str): Starting address or coordinates
            - destination (str): Ending address or coordinates
            - travel_mode (TravelMode): DRIVE, WALK, BICYCLE, TRANSIT, TWO_WHEELER (default: DRIVE)
            - departure_time (Optional[str]): ISO 8601 time for traffic-aware routing
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Route information with distance and duration

        Success response (markdown):
            # Route: [Origin] → [Destination]
            Travel Mode: [mode]

            ## Summary
            - **Distance**: X.X miles (X.X km)
            - **Duration**: Xh Xm (in current traffic)
            - **Duration without traffic**: Xh Xm

            ## Route Instructions
            1. [Step 1 instruction]
            2. [Step 2 instruction]
            ...

        Success response (json):
            {
                "origin": str,
                "destination": str,
                "travel_mode": str,
                "distance_miles": float,
                "distance_meters": int,
                "duration_seconds": int,
                "duration_formatted": str,
                "duration_in_traffic_seconds": int,
                "steps": [{"instruction": str, "distance": str, "duration": str}]
            }

        Error response:
            "Error: [error message]"

    Examples:
        - Use when: "How far is the facility from Savannah airport?"
        - Use when: "What's the drive time to Memorial Health Hospital?"
        - Use when: "Calculate distance to downtown Savannah"
        - Use when: "Get drive time with morning rush hour traffic"
        - Don't use when: Comparing multiple locations (use distance_matrix)

    Error Handling:
        - Returns "Error: API key not configured" if GOOGLE_MAPS_API_KEY not set
        - Returns "Error: No route found" if locations are unreachable
        - Returns formatted route info or error message
    '''
    if not _check_api_key():
        return "Error: Google Maps API key not configured. Please set the GOOGLE_MAPS_API_KEY environment variable."

    try:
        request_body = {
            "origin": {"address": params.origin},
            "destination": {"address": params.destination},
            "travelMode": params.travel_mode.value,
            "computeAlternativeRoutes": False,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "requestedReferenceRoutes": ["FUEL_EFFICIENT"]
        }

        # Add departure time if provided
        if params.departure_time:
            request_body["departureTime"] = params.departure_time

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ROUTES_API_BASE_URL}/directions/v2:computeRoutes",
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": API_KEY,
                    "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline,routes.legs.steps,routes.legs.localizedValues,routes.legs.distanceMeters,routes.legs.duration,routes.legs.staticDuration"
                },
                json=request_body,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        routes = data.get("routes", [])
        if not routes:
            return f"No route found between '{params.origin}' and '{params.destination}'"

        route = routes[0]
        leg = route.get("legs", [{}])[0]

        distance_meters = leg.get("distanceMeters", 0)
        distance_miles = _meters_to_miles(distance_meters)
        duration_seconds = int(leg.get("duration", "0s").replace("s", ""))
        static_duration = int(leg.get("staticDuration", "0s").replace("s", ""))

        # Get steps
        steps = leg.get("steps", [])
        instructions = []
        for i, step in enumerate(steps, 1):
            nav_instruction = step.get("navigationInstruction", {})
            instructions.append({
                "step_number": i,
                "instruction": nav_instruction.get("instructions", "Continue"),
                "distance": _meters_to_miles(step.get("distanceMeters", 0)),
                "duration": _format_duration(int(step.get("duration", "0s").replace("s", "")))
            })

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [
                f"# Route: {params.origin} → {params.destination}",
                f"Travel Mode: {params.travel_mode.value}",
                "",
                "## Summary",
                f"- **Distance**: {distance_miles:.2f} miles ({distance_meters:,} meters)",
                f"- **Duration**: {_format_duration(duration_seconds)}"
            ]

            if static_duration and static_duration != duration_seconds:
                lines.append(f"- **Duration without traffic**: {_format_duration(static_duration)}")
                traffic_delay = duration_seconds - static_duration
                if traffic_delay > 0:
                    lines.append(f"- **Traffic delay**: +{_format_duration(traffic_delay)}")

            lines.append("")

            if instructions:
                lines.append("## Route Instructions")
                for instr in instructions:
                    lines.append(f"{instr['step_number']}. {instr['instruction']} - {instr['distance']:.1f} mi ({instr['duration']})")
                lines.append("")

            result = "\n".join(lines)
        else:
            result = json.dumps({
                "origin": params.origin,
                "destination": params.destination,
                "travel_mode": params.travel_mode.value,
                "distance_miles": round(distance_miles, 2),
                "distance_meters": distance_meters,
                "duration_seconds": duration_seconds,
                "duration_formatted": _format_duration(duration_seconds),
                "static_duration_seconds": static_duration,
                "steps": instructions
            }, indent=2)

        return result

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="google_routes_compute_distance_matrix",
    annotations={
        "title": "Calculate Distance Matrix for Multiple Locations",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def google_routes_compute_distance_matrix(params: DistanceMatrixInput) -> str:
    '''
    Calculate distances and travel times between multiple origin and destination pairs.

    This tool efficiently computes distances and durations for multiple combinations of
    origins and destinations in a single request. Useful for comparing multiple facilities
    or analyzing accessibility from various starting points.

    Args:
        params (DistanceMatrixInput): Validated input parameters containing:
            - origins (List[str]): Starting addresses (max 25)
            - destinations (List[str]): Destination addresses (max 25)
            - travel_mode (TravelMode): DRIVE, WALK, BICYCLE, TRANSIT (default: DRIVE)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Distance matrix results

        Success response (markdown):
            # Distance Matrix
            Origins: X | Destinations: Y | Travel Mode: [mode]

            ## Results

            ### From: [Origin 1]
            To [Destination 1]: X.X mi, Xh Xm
            To [Destination 2]: X.X mi, Xh Xm

            ### From: [Origin 2]
            ...

        Success response (json):
            {
                "origins": List[str],
                "destinations": List[str],
                "travel_mode": str,
                "matrix": [
                    {
                        "origin": str,
                        "destination": str,
                        "distance_miles": float,
                        "duration_formatted": str,
                        "duration_seconds": int
                    }
                ]
            }

        Error response:
            "Error: [error message]"

    Examples:
        - Use when: "Compare distances from 3 properties to 5 hospitals"
        - Use when: "Calculate drive times from facility to multiple airports"
        - Use when: "Analyze accessibility from different neighborhoods"
        - Don't use when: Only calculating one route (use compute_route)

    Error Handling:
        - Returns "Error: API key not configured" if GOOGLE_MAPS_API_KEY not set
        - Returns "Error: Too many locations" if limits exceeded
        - Some routes may be unavailable (marked in results)
    '''
    if not _check_api_key():
        return "Error: Google Maps API key not configured. Please set the GOOGLE_MAPS_API_KEY environment variable."

    try:
        # Validate limits
        if len(params.origins) * len(params.destinations) > 100:
            return "Error: Too many origin-destination combinations (max 100). Reduce the number of origins or destinations."

        request_body = {
            "origins": [{"address": origin} for origin in params.origins],
            "destinations": [{"address": dest} for dest in params.destinations],
            "travelMode": params.travel_mode.value
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ROUTES_API_BASE_URL}/distanceMatrix/v2:computeRouteMatrix",
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": API_KEY,
                    "X-Goog-FieldMask": "originIndex,destinationIndex,distanceMeters,duration,status,condition"
                },
                json=request_body,
                timeout=60.0  # Longer timeout for matrix calculations
            )
            response.raise_for_status()

            # Routes API returns streaming JSON-L format for distance matrix
            results = []
            for line in response.text.strip().split('\n'):
                if line:
                    results.append(json.loads(line))

        # Process results
        matrix = []
        for result in results:
            origin_idx = result.get("originIndex", 0)
            dest_idx = result.get("destinationIndex", 0)
            status = result.get("status")

            if origin_idx < len(params.origins) and dest_idx < len(params.destinations):
                origin = params.origins[origin_idx]
                destination = params.destinations[dest_idx]

                if status == "OK":
                    distance_meters = result.get("distanceMeters", 0)
                    distance_miles = _meters_to_miles(distance_meters)
                    duration_seconds = int(result.get("duration", "0s").replace("s", ""))

                    matrix.append({
                        "origin": origin,
                        "destination": destination,
                        "distance_miles": round(distance_miles, 2),
                        "distance_meters": distance_meters,
                        "duration_seconds": duration_seconds,
                        "duration_formatted": _format_duration(duration_seconds),
                        "status": "OK"
                    })
                else:
                    matrix.append({
                        "origin": origin,
                        "destination": destination,
                        "status": "UNAVAILABLE",
                        "error": result.get("condition", "No route found")
                    })

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [
                "# Distance Matrix",
                f"Origins: {len(params.origins)} | Destinations: {len(params.destinations)} | Travel Mode: {params.travel_mode.value}",
                "",
                "## Results",
                ""
            ]

            # Group by origin
            for origin in params.origins:
                lines.append(f"### From: {origin}")
                origin_results = [r for r in matrix if r["origin"] == origin]

                for result in origin_results:
                    if result.get("status") == "OK":
                        lines.append(f"- To **{result['destination']}**: {result['distance_miles']} mi, {result['duration_formatted']}")
                    else:
                        lines.append(f"- To **{result['destination']}**: Route unavailable ({result.get('error', 'Unknown error')})")

                lines.append("")

            result_text = "\n".join(lines)
        else:
            result_text = json.dumps({
                "origins": params.origins,
                "destinations": params.destinations,
                "travel_mode": params.travel_mode.value,
                "total_combinations": len(params.origins) * len(params.destinations),
                "matrix": matrix
            }, indent=2)

        # Check character limit
        if len(result_text) > CHARACTER_LIMIT:
            truncation_note = f"\n\n[Response truncated - exceeded {CHARACTER_LIMIT} character limit. Try reducing the number of origins or destinations.]"
            result_text = result_text[:CHARACTER_LIMIT - len(truncation_note)] + truncation_note

        return result_text

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="google_geocoding_geocode",
    annotations={
        "title": "Geocode Address to Coordinates",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def google_geocoding_geocode(params: GeocodeInput) -> str:
    '''
    Convert an address to geographic coordinates (latitude/longitude).

    This tool validates and geocodes addresses, returning precise coordinates and
    formatted address information. Useful for verifying property addresses and
    getting coordinates for mapping and distance calculations.

    Args:
        params (GeocodeInput): Validated input parameters containing:
            - address (str): Address to geocode (e.g., '249 Holland Drive, Savannah, GA 31419')
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Geocoded address information with coordinates

        Success response (markdown):
            # Geocoding Result

            ## Address
            **Input**: [original address]
            **Formatted**: [Google's formatted address]

            ## Coordinates
            - **Latitude**: X.XXXXXX
            - **Longitude**: Y.YYYYYY

            ## Location Details
            - [Address components]

        Success response (json):
            {
                "input_address": str,
                "formatted_address": str,
                "coordinates": {"latitude": float, "longitude": float},
                "address_components": [...],
                "location_type": str,
                "place_id": str
            }

        Error response:
            "Error: [error message]"

    Examples:
        - Use when: "Validate the address 249 Holland Drive, Savannah, GA"
        - Use when: "Get coordinates for Memorial Health Hospital"
        - Use when: "Convert facility address to lat/lng"
        - Don't use when: You have coordinates (use reverse_geocode)

    Error Handling:
        - Returns "Error: API key not configured" if GOOGLE_MAPS_API_KEY not set
        - Returns "Error: Address not found" if address is invalid
        - Returns geocoded info or error message
    '''
    if not _check_api_key():
        return "Error: Google Maps API key not configured. Please set the GOOGLE_MAPS_API_KEY environment variable."

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GEOCODING_API_BASE_URL}/json",
                params={
                    "address": params.address,
                    "key": API_KEY
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        if data.get("status") != "OK":
            return f"Error: Could not geocode address '{params.address}'. Status: {data.get('status')}"

        result = data.get("results", [{}])[0]
        coords = result.get("geometry", {}).get("location", {})

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [
                "# Geocoding Result",
                "",
                "## Address",
                f"**Input**: {params.address}",
                f"**Formatted**: {result.get('formatted_address', 'N/A')}",
                "",
                "## Coordinates",
                f"- **Latitude**: {coords.get('lat')}",
                f"- **Longitude**: {coords.get('lng')}",
                ""
            ]

            # Add location details
            components = result.get("address_components", [])
            if components:
                lines.append("## Location Details")
                for component in components:
                    types = ", ".join(component.get("types", []))
                    lines.append(f"- **{component.get('long_name')}** ({types})")
                lines.append("")

            lines.append(f"**Location Type**: {result.get('geometry', {}).get('location_type', 'N/A')}")
            lines.append(f"**Place ID**: {result.get('place_id', 'N/A')}")

            result_text = "\n".join(lines)
        else:
            result_text = json.dumps({
                "input_address": params.address,
                "formatted_address": result.get("formatted_address"),
                "coordinates": {
                    "latitude": coords.get("lat"),
                    "longitude": coords.get("lng")
                },
                "address_components": result.get("address_components"),
                "location_type": result.get("geometry", {}).get("location_type"),
                "place_id": result.get("place_id")
            }, indent=2)

        return result_text

    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="google_geocoding_reverse_geocode",
    annotations={
        "title": "Reverse Geocode Coordinates to Address",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def google_geocoding_reverse_geocode(params: ReverseGeocodeInput) -> str:
    '''
    Convert geographic coordinates to a human-readable address.

    This tool performs reverse geocoding, converting latitude/longitude coordinates
    into addresses and location information. Useful for interpreting coordinates from
    maps or GPS data.

    Args:
        params (ReverseGeocodeInput): Validated input parameters containing:
            - latitude (float): Latitude coordinate (-90 to 90)
            - longitude (float): Longitude coordinate (-180 to 180)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Address information for the coordinates

        Success response (markdown):
            # Reverse Geocoding Result

            ## Coordinates
            Latitude: X.XXXXXX, Longitude: Y.YYYYYY

            ## Address
            [Formatted address]

            ## Location Details
            [Address components]

        Success response (json):
            {
                "coordinates": {"latitude": float, "longitude": float},
                "formatted_address": str,
                "address_components": [...],
                "place_id": str
            }

        Error response:
            "Error: [error message]"

    Examples:
        - Use when: "What address is at coordinates 32.0809, -81.0912?"
        - Use when: "Convert lat/lng to street address"
        - Don't use when: You have an address (use geocode)

    Error Handling:
        - Returns "Error: API key not configured" if GOOGLE_MAPS_API_KEY not set
        - Returns "Error: No address found" if coordinates are in ocean/remote area
        - Returns address info or error message
    '''
    if not _check_api_key():
        return "Error: Google Maps API key not configured. Please set the GOOGLE_MAPS_API_KEY environment variable."

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GEOCODING_API_BASE_URL}/json",
                params={
                    "latlng": f"{params.latitude},{params.longitude}",
                    "key": API_KEY
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        if data.get("status") != "OK":
            return f"Error: Could not reverse geocode coordinates ({params.latitude}, {params.longitude}). Status: {data.get('status')}"

        result = data.get("results", [{}])[0]

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [
                "# Reverse Geocoding Result",
                "",
                "## Coordinates",
                f"Latitude: {params.latitude}, Longitude: {params.longitude}",
                "",
                "## Address",
                result.get("formatted_address", "N/A"),
                ""
            ]

            # Add location details
            components = result.get("address_components", [])
            if components:
                lines.append("## Location Details")
                for component in components:
                    types = ", ".join(component.get("types", []))
                    lines.append(f"- **{component.get('long_name')}** ({types})")
                lines.append("")

            lines.append(f"**Place ID**: {result.get('place_id', 'N/A')}")

            result_text = "\n".join(lines)
        else:
            result_text = json.dumps({
                "coordinates": {
                    "latitude": params.latitude,
                    "longitude": params.longitude
                },
                "formatted_address": result.get("formatted_address"),
                "address_components": result.get("address_components"),
                "place_id": result.get("place_id")
            }, indent=2)

        return result_text

    except Exception as e:
        return _handle_api_error(e)

if __name__ == "__main__":
    mcp.run()
