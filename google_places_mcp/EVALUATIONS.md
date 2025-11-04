# Google Places MCP Server - Evaluation Guide

This document provides guidance on creating evaluations to test the effectiveness of the MCP server.

## Purpose of Evaluations

Evaluations test whether LLMs can effectively use the MCP server to answer realistic, complex questions about property research and area analysis. They verify that the tools work together to enable complete workflows.

## Evaluation Requirements

Each evaluation question must be:
- **Independent**: Not dependent on other questions
- **Read-only**: Only non-destructive operations required
- **Complex**: Requiring multiple tool calls and deep exploration
- **Realistic**: Based on real use cases from property research
- **Verifiable**: Single, clear answer that can be verified
- **Stable**: Answer won't change over time (use specific addresses/Place IDs)

## Sample Evaluation Questions

### Category 1: Distance & Accessibility Analysis

#### Q1: Hospital Distance Verification
**Question**: What is the exact driving distance in miles from 249 Holland Drive, Savannah, GA 31419 to the nearest hospital?

**Expected Process**:
1. Use `google_places_nearby_search` with location="249 Holland Drive, Savannah, GA 31419", place_types=["hospital"], radius_miles=10
2. Identify the closest hospital by distance
3. Use `google_routes_compute_route` with origin and destination to get exact driving distance
4. Extract distance in miles from the response

**Answer Format**: "X.X miles"

**Why this works**: Tests integration of search and routing, requires comparing distances and extracting specific values.

---

#### Q2: Airport Drive Time with Traffic
**Question**: What is the driving time from 249 Holland Drive, Savannah, GA 31419 to Savannah/Hilton Head International Airport during midday traffic?

**Expected Process**:
1. Use `google_routes_compute_route` with appropriate parameters
2. Extract duration from response

**Answer Format**: "X minutes" or "Xh Xm"

**Why this works**: Tests route calculation with single query, verifiable answer.

---

### Category 2: Place Discovery & Quality

#### Q3: Highest Rated Hospital
**Question**: Among hospitals within 15 miles of 249 Holland Drive, Savannah, GA 31419, which one has the highest Google rating?

**Expected Process**:
1. Use `google_places_nearby_search` with radius_miles=15, place_types=["hospital"]
2. Compare ratings from all results
3. Identify hospital with highest rating

**Answer Format**: "Hospital Name (X.X stars)"

**Why this works**: Tests search, data extraction, and comparison across multiple results.

---

#### Q4: Hotel Review Analysis
**Question**: What is the most common complaint mentioned in reviews for hotels within 5 miles of 249 Holland Drive, Savannah, GA 31419 rated below 4.0 stars?

**Expected Process**:
1. Use `google_places_nearby_search` to find hotels within 5 miles
2. Filter results to those with rating < 4.0
3. For each, use `google_places_get_details` with include_reviews=True
4. Analyze review text for common themes
5. Identify most frequent complaint

**Answer Format**: "Most common complaint: [theme]"

**Why this works**: Complex workflow requiring search, filtering, detail lookup, and content analysis.

---

### Category 3: Comparative Analysis

#### Q5: Distance Matrix Analysis
**Question**: Which of these three locations is closest by driving distance to downtown Savannah: 249 Holland Drive, Savannah Airport, or Memorial Health Hospital?

**Expected Process**:
1. First geocode "downtown Savannah" to get specific coordinates
2. Use `google_routes_compute_distance_matrix` with the three locations as origins and downtown as destination
3. Compare distances
4. Identify the closest

**Answer Format**: "Location Name (X.X miles)"

**Why this works**: Tests distance matrix tool and comparison logic.

---

### Category 4: Amenity Accessibility

#### Q6: Dining Options Count
**Question**: How many restaurants with a rating of 4.0 or higher are within a 3-mile radius of 249 Holland Drive, Savannah, GA 31419?

**Expected Process**:
1. Use `google_places_nearby_search` with place_types=["restaurant"], radius_miles=3
2. Filter results where rating >= 4.0
3. Count the results

**Answer Format**: "X restaurants"

**Why this works**: Tests search with specific criteria and counting/filtering.

---

### Category 5: Address Validation

#### Q7: Coordinate Precision
**Question**: What is the latitude (to 4 decimal places) of 249 Holland Drive, Savannah, GA 31419?

**Expected Process**:
1. Use `google_geocoding_geocode` with the address
2. Extract latitude from coordinates
3. Round to 4 decimal places

**Answer Format**: "XX.XXXX"

**Why this works**: Tests geocoding accuracy and precision.

---

### Category 6: Complex Multi-Step Analysis

#### Q8: Healthcare Quality Assessment
**Question**: What is the Google rating of the closest hospital to 249 Holland Drive, Savannah, GA 31419, and how many user reviews does it have?

**Expected Process**:
1. Use `google_places_nearby_search` to find hospitals
2. Identify closest by distance_miles
3. Note the place_id
4. Use `google_places_get_details` to get full information
5. Extract rating and review count

**Answer Format**: "Hospital Name: X.X stars (Y reviews)"

**Why this works**: Multi-step workflow combining search, comparison, and detailed lookup.

---

#### Q9: Place Type Discovery
**Question**: What is the primary type (category) of the place with Place ID ChIJN1t_tDeuEmsRUsoyG83frY4?

**Expected Process**:
1. Use `google_places_get_details` with the Place ID
2. Extract types list
3. Return the first (primary) type

**Answer Format**: "Primary type: [type]"

**Why this works**: Tests direct place lookup by ID.

---

#### Q10: Comprehensive Area Assessment
**Question**: Within 10 miles of 249 Holland Drive, Savannah, GA 31419, how many of each are there: hospitals, hotels, and parks?

**Expected Process**:
1. Use `google_places_nearby_search` three times with different place_types
2. Count results for each category
3. Format the counts

**Answer Format**: "Hospitals: X, Hotels: Y, Parks: Z"

**Why this works**: Tests ability to make multiple searches and aggregate results.

---

## Creating Your Own Evaluations

### Step 1: Choose a Realistic Scenario
Think about actual property research questions:
- Distance to key amenities
- Quality ratings and reviews
- Accessibility comparisons
- Address validation needs

### Step 2: Design the Question
Make it:
- Specific (use real addresses)
- Complex (require 2-4 tool calls)
- Verifiable (one clear answer)

### Step 3: Manually Solve It
Before adding to evaluation set:
1. Use the tools yourself to answer the question
2. Document the exact steps taken
3. Record the answer with source timestamps
4. Verify answer is stable over time

### Step 4: Format as XML (Optional)
```xml
<evaluation>
  <qa_pair>
    <question>What is the exact driving distance in miles from 249 Holland Drive, Savannah, GA 31419 to the nearest hospital?</question>
    <answer>5.8 miles</answer>
  </qa_pair>
  <!-- More qa_pairs... -->
</evaluation>
```

## Running Evaluations

### Prerequisites
- Valid `GOOGLE_MAPS_API_KEY` configured
- MCP server running and connected
- Claude or another MCP client

### Manual Testing Process
1. Start a conversation with Claude (with MCP server connected)
2. Ask each evaluation question
3. Verify Claude uses the correct tools
4. Compare final answer to expected answer
5. Document any issues or improvements needed

### Automated Testing (Advanced)
For automated evaluation, you would need:
- MCP client library
- Test harness to invoke tools
- Answer comparison logic
- Results reporting

## Success Criteria

An evaluation passes if:
- ✅ Correct tools are used in logical order
- ✅ Parameters are appropriate for the query
- ✅ Final answer matches expected answer (allowing for minor rounding)
- ✅ No errors occur during tool execution
- ✅ Response is completed within reasonable time

An evaluation fails if:
- ❌ Wrong tools are used
- ❌ Incorrect parameters provided
- ❌ Answer is significantly different
- ❌ Errors occur that prevent completion
- ❌ Response times out or gets stuck

## Notes on Answer Stability

### Stable Answers (Good for Evaluations)
- Distances between fixed addresses
- Coordinates of specific addresses
- Place IDs and types
- Historical ratings (with date qualifier)

### Unstable Answers (Avoid for Evaluations)
- "Current" ratings (change over time)
- "Open now" status (depends on time)
- Number of reviews (increases over time)
- Traffic times (vary by time/date)
- "Nearest" without fixed radius (new places open)

### Making Unstable Answers Stable
Instead of: "What is the current rating of X?"
Use: "What was the rating of X on 2025-11-03?"

Instead of: "How long does it take to get to X?"
Use: "What is the distance in miles to X?" (distance is more stable)

## Continuous Improvement

Use evaluation results to:
1. Identify which tools work well together
2. Find edge cases that need better error handling
3. Improve tool descriptions and examples
4. Add new tools for common patterns
5. Optimize response formats for clarity

---

**Note**: Actual evaluation runs require a valid Google Maps API key and will consume API quota. Plan accordingly and monitor usage in Google Cloud Console.
