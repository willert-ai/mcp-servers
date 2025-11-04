"""
Google Maps MCP Server
Provides location analysis tools for memory care facility research

Functions:
- get_distance: Calculate distance between two locations
- get_drive_time: Calculate drive time with optional traffic consideration
- search_nearby: Find nearby places of specific type
- get_place_details: Get detailed information about a specific place
- validate_address: Validate and standardize an address

APIs Used:
- Google Maps Directions API
- Google Maps Distance Matrix API
- Google Maps Places API
- Google Maps Geocoding API

Free Tier: $200 monthly credit (≈40,000 Directions requests/month)
"""

from fastmcp import FastMCP
import os
import googlemaps
from datetime import datetime
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("google-maps")

# Initialize Google Maps client
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable is required")

gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)


@mcp.tool()
def get_distance(
    origin: str,
    destination: str,
    mode: str = "driving"
) -> Dict[str, Any]:
    """
    Calculate distance between two locations

    Args:
        origin: Starting location (address or place name)
        destination: Ending location (address or place name)
        mode: Travel mode (driving, walking, bicycling, transit)

    Returns:
        Dictionary with distance in miles and meters, plus formatted text

    Example:
        get_distance("249 Holland Drive, Savannah, GA 31419", "Memorial Health University Medical Center, Savannah, GA", "driving")
    """
    try:
        result = gmaps.distance_matrix(
            origins=[origin],
            destinations=[destination],
            mode=mode,
            units="imperial"
        )

        if result['rows'][0]['elements'][0]['status'] == 'OK':
            element = result['rows'][0]['elements'][0]
            distance_text = element['distance']['text']
            distance_meters = element['distance']['value']
            distance_miles = distance_meters / 1609.34

            return {
                "status": "success",
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "distance_miles": round(distance_miles, 2),
                "distance_meters": distance_meters,
                "distance_formatted": distance_text,
                "source": "Google Maps Distance Matrix API",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "error",
                "error": result['rows'][0]['elements'][0]['status'],
                "message": "Unable to calculate distance"
            }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_drive_time(
    origin: str,
    destination: str,
    time_of_day: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate drive time between two locations with optional traffic consideration

    Args:
        origin: Starting location (address or place name)
        destination: Ending location (address or place name)
        time_of_day: Optional time to consider traffic (format: "YYYY-MM-DD HH:MM" or "now")

    Returns:
        Dictionary with duration in minutes, formatted text, and traffic consideration

    Example:
        get_drive_time("249 Holland Drive, Savannah, GA 31419", "Savannah/Hilton Head International Airport", "now")
    """
    try:
        departure_time = None
        if time_of_day:
            if time_of_day.lower() == "now":
                departure_time = datetime.now()
            else:
                try:
                    departure_time = datetime.strptime(time_of_day, "%Y-%m-%d %H:%M")
                except ValueError:
                    return {
                        "status": "error",
                        "error": "Invalid time_of_day format. Use 'YYYY-MM-DD HH:MM' or 'now'"
                    }

        result = gmaps.directions(
            origin=origin,
            destination=destination,
            mode="driving",
            departure_time=departure_time
        )

        if result:
            leg = result[0]['legs'][0]
            duration_text = leg['duration']['text']
            duration_seconds = leg['duration']['value']
            duration_minutes = duration_seconds / 60

            # Check if duration_in_traffic is available
            traffic_duration_minutes = None
            if 'duration_in_traffic' in leg:
                traffic_duration_seconds = leg['duration_in_traffic']['value']
                traffic_duration_minutes = traffic_duration_seconds / 60

            response = {
                "status": "success",
                "origin": origin,
                "destination": destination,
                "duration_minutes": round(duration_minutes, 1),
                "duration_formatted": duration_text,
                "distance_miles": round(leg['distance']['value'] / 1609.34, 2),
                "distance_formatted": leg['distance']['text'],
                "source": "Google Maps Directions API",
                "timestamp": datetime.utcnow().isoformat()
            }

            if traffic_duration_minutes:
                response["duration_with_traffic_minutes"] = round(traffic_duration_minutes, 1)
                response["traffic_delay_minutes"] = round(traffic_duration_minutes - duration_minutes, 1)

            return response
        else:
            return {
                "status": "error",
                "error": "No route found"
            }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def search_nearby(
    location: str,
    place_type: str = "hospital",
    radius_miles: float = 10.0,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Find nearby places of a specific type

    Args:
        location: Center point for search (address or place name)
        place_type: Type of place to search for (hospital, pharmacy, restaurant, park, etc.)
        radius_miles: Search radius in miles (max 31 miles)
        limit: Maximum number of results to return (max 20)

    Returns:
        Dictionary with list of nearby places including name, address, distance, rating

    Example:
        search_nearby("249 Holland Drive, Savannah, GA 31419", "hospital", 10.0, 5)
    """
    try:
        # First geocode the location to get coordinates
        geocode_result = gmaps.geocode(location)
        if not geocode_result:
            return {
                "status": "error",
                "error": f"Could not geocode location: {location}"
            }

        center_coords = geocode_result[0]['geometry']['location']
        radius_meters = radius_miles * 1609.34

        # Limit radius to API maximum (50km)
        if radius_meters > 50000:
            radius_meters = 50000
            radius_miles = 31.07

        # Search for nearby places
        places_result = gmaps.places_nearby(
            location=center_coords,
            radius=radius_meters,
            type=place_type
        )

        places = []
        for place in places_result.get('results', [])[:limit]:
            place_info = {
                "name": place.get('name'),
                "address": place.get('vicinity'),
                "place_id": place.get('place_id'),
                "rating": place.get('rating'),
                "user_ratings_total": place.get('user_ratings_total'),
                "types": place.get('types', [])
            }

            # Calculate distance from center
            place_coords = place['geometry']['location']
            distance_result = gmaps.distance_matrix(
                origins=[center_coords],
                destinations=[place_coords],
                mode="driving",
                units="imperial"
            )

            if distance_result['rows'][0]['elements'][0]['status'] == 'OK':
                element = distance_result['rows'][0]['elements'][0]
                place_info['distance_miles'] = round(element['distance']['value'] / 1609.34, 2)
                place_info['drive_time_minutes'] = round(element['duration']['value'] / 60, 1)

            places.append(place_info)

        # Sort by distance
        places.sort(key=lambda x: x.get('distance_miles', float('inf')))

        return {
            "status": "success",
            "search_center": location,
            "place_type": place_type,
            "radius_miles": radius_miles,
            "total_found": len(places),
            "places": places,
            "source": "Google Maps Places API",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def get_place_details(place_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific place

    Args:
        place_id: Google Places ID for the location

    Returns:
        Dictionary with detailed place information including rating, reviews, hours, phone

    Example:
        get_place_details("ChIJN1t_tDeuEmsRUsoyG83frY4")
    """
    try:
        result = gmaps.place(place_id=place_id)

        if result['status'] == 'OK':
            place = result['result']

            details = {
                "status": "success",
                "name": place.get('name'),
                "address": place.get('formatted_address'),
                "phone": place.get('formatted_phone_number'),
                "website": place.get('website'),
                "rating": place.get('rating'),
                "user_ratings_total": place.get('user_ratings_total'),
                "price_level": place.get('price_level'),
                "types": place.get('types', []),
                "place_id": place_id,
                "source": "Google Maps Places API",
                "timestamp": datetime.utcnow().isoformat()
            }

            # Add opening hours if available
            if 'opening_hours' in place:
                details['opening_hours'] = {
                    "open_now": place['opening_hours'].get('open_now'),
                    "weekday_text": place['opening_hours'].get('weekday_text', [])
                }

            # Add reviews (top 5) if available
            if 'reviews' in place:
                details['reviews'] = [
                    {
                        "author": review.get('author_name'),
                        "rating": review.get('rating'),
                        "text": review.get('text'),
                        "time": review.get('relative_time_description')
                    }
                    for review in place['reviews'][:5]
                ]

            return details
        else:
            return {
                "status": "error",
                "error": result['status'],
                "message": "Unable to get place details"
            }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def validate_address(address: str) -> Dict[str, Any]:
    """
    Validate and standardize an address using geocoding

    Args:
        address: Address to validate

    Returns:
        Dictionary with validated address, coordinates, and address components

    Example:
        validate_address("249 Holland Drive, Savannah, Georgia 31419")
    """
    try:
        result = gmaps.geocode(address)

        if result:
            location = result[0]

            # Extract address components
            components = {}
            for component in location.get('address_components', []):
                for comp_type in component['types']:
                    components[comp_type] = component.get('long_name')

            return {
                "status": "success",
                "input_address": address,
                "formatted_address": location.get('formatted_address'),
                "latitude": location['geometry']['location']['lat'],
                "longitude": location['geometry']['location']['lng'],
                "place_id": location.get('place_id'),
                "location_type": location['geometry'].get('location_type'),
                "address_components": {
                    "street_number": components.get('street_number'),
                    "street": components.get('route'),
                    "city": components.get('locality'),
                    "county": components.get('administrative_area_level_2'),
                    "state": components.get('administrative_area_level_1'),
                    "state_code": [c.get('short_name') for c in location.get('address_components', [])
                                   if 'administrative_area_level_1' in c['types']][0] if location.get('address_components') else None,
                    "zip_code": components.get('postal_code'),
                    "country": components.get('country')
                },
                "source": "Google Maps Geocoding API",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "error",
                "error": "Address not found",
                "message": f"Could not validate address: {address}"
            }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
