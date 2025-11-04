#!/usr/bin/env python3
"""
Perplexity MCP Server

This server provides tools to interact with the Perplexity AI API, including
chat completions, web search, deep research, and reasoning capabilities using
the latest Perplexity models (sonar, sonar-pro, sonar-deep-research, sonar-reasoning).
"""

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
mcp = FastMCP("perplexity-mcp")

# Constants
API_BASE_URL = "https://api.perplexity.ai"
CHARACTER_LIMIT = 25000  # Maximum response size in characters
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 4096


# Enums
class PerplexityModel(str, Enum):
    """Available Perplexity AI models."""
    SONAR = "sonar"
    SONAR_PRO = "sonar-pro"
    SONAR_DEEP_RESEARCH = "sonar-deep-research"
    SONAR_REASONING = "sonar-reasoning"
    SONAR_REASONING_PRO = "sonar-reasoning-pro"


class SearchMode(str, Enum):
    """Search modes for Perplexity API."""
    WEB = "web"
    ACADEMIC = "academic"
    SEC = "sec"


class ReasoningEffort(str, Enum):
    """Reasoning effort levels for deep research."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Pydantic Models for Input Validation
class PerplexityAskInput(BaseModel):
    """Input model for general chat completions with Perplexity AI."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    query: str = Field(
        ...,
        description="The question or prompt to ask Perplexity AI (e.g., 'What are the latest developments in quantum computing?')",
        min_length=1,
        max_length=10000
    )
    model: PerplexityModel = Field(
        default=PerplexityModel.SONAR_PRO,
        description="Model to use: 'sonar' (lightweight), 'sonar-pro' (advanced, default)"
    )
    search_mode: Optional[SearchMode] = Field(
        default=SearchMode.WEB,
        description="Search mode: 'web' (default), 'academic' (scholarly sources), 'sec' (SEC filings)"
    )
    return_citations: bool = Field(
        default=True,
        description="Whether to include citations and sources in the response"
    )
    return_images: bool = Field(
        default=False,
        description="Whether to include relevant images in the response"
    )
    return_related_questions: bool = Field(
        default=False,
        description="Whether to suggest related follow-up questions"
    )
    max_tokens: Optional[int] = Field(
        default=DEFAULT_MAX_TOKENS,
        description="Maximum tokens in response (default: 4096)",
        ge=1,
        le=16384
    )
    temperature: Optional[float] = Field(
        default=DEFAULT_TEMPERATURE,
        description="Temperature for randomness (0.0-2.0, default: 0.2)",
        ge=0.0,
        le=2.0
    )

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()


class PerplexitySearchInput(BaseModel):
    """Input model for focused web search with Perplexity AI."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    query: str = Field(
        ...,
        description="Search query (e.g., 'latest AI research papers 2025', 'Tesla stock analysis')",
        min_length=1,
        max_length=500
    )
    search_mode: SearchMode = Field(
        default=SearchMode.WEB,
        description="Search mode: 'web' (default), 'academic' (scholarly), 'sec' (SEC filings)"
    )
    search_recency_filter: Optional[str] = Field(
        default=None,
        description="Temporal filter: 'day', 'week', 'month', 'year' (e.g., 'week' for results from past week)"
    )
    search_domain_filter: Optional[List[str]] = Field(
        default=None,
        description="Filter by domains - use '+' to allow, '-' to block (e.g., ['+nytimes.com', '-wikipedia.org']). Max 20 domains.",
        max_length=20
    )
    return_images: bool = Field(
        default=True,
        description="Whether to include relevant images in search results"
    )
    return_related_questions: bool = Field(
        default=True,
        description="Whether to suggest related follow-up questions"
    )

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()

    @field_validator('search_domain_filter')
    @classmethod
    def validate_domain_filter(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None and len(v) > 20:
            raise ValueError("Maximum 20 domains allowed in search_domain_filter")
        return v


class PerplexityResearchInput(BaseModel):
    """Input model for deep exhaustive research with Perplexity AI."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    research_query: str = Field(
        ...,
        description="Research topic for comprehensive analysis (e.g., 'Impact of AI on healthcare in 2024-2025')",
        min_length=10,
        max_length=1000
    )
    reasoning_effort: ReasoningEffort = Field(
        default=ReasoningEffort.HIGH,
        description="Research depth: 'low', 'medium', 'high' (default: 'high' for most thorough analysis)"
    )
    search_mode: SearchMode = Field(
        default=SearchMode.WEB,
        description="Source type: 'web' (default), 'academic' (scholarly sources), 'sec' (SEC filings)"
    )
    return_images: bool = Field(
        default=True,
        description="Whether to include relevant images and visualizations"
    )

    @field_validator('research_query')
    @classmethod
    def validate_research_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Research query cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("Research query too short - please provide more detail (minimum 10 characters)")
        return v.strip()


class PerplexityReasonInput(BaseModel):
    """Input model for reasoning and problem-solving with Perplexity AI."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    problem: str = Field(
        ...,
        description="Problem or question requiring logical reasoning (e.g., 'Analyze the pros and cons of remote work for tech companies')",
        min_length=10,
        max_length=5000
    )
    model: PerplexityModel = Field(
        default=PerplexityModel.SONAR_REASONING_PRO,
        description="Reasoning model: 'sonar-reasoning' (fast), 'sonar-reasoning-pro' (premier, default)"
    )
    temperature: Optional[float] = Field(
        default=0.0,
        description="Temperature for determinism (0.0 for most logical, up to 2.0 for creative)",
        ge=0.0,
        le=2.0
    )

    @field_validator('problem')
    @classmethod
    def validate_problem(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Problem cannot be empty")
        return v.strip()

    @field_validator('model')
    @classmethod
    def validate_model(cls, v: PerplexityModel) -> PerplexityModel:
        if v not in [PerplexityModel.SONAR_REASONING, PerplexityModel.SONAR_REASONING_PRO]:
            raise ValueError(f"Model must be either '{PerplexityModel.SONAR_REASONING.value}' or '{PerplexityModel.SONAR_REASONING_PRO.value}' for reasoning tasks")
        return v


# Shared utility functions
def _get_api_key() -> str:
    """Get Perplexity API key from environment variables."""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY not set in .env file")
    return api_key


async def _make_api_request(
    endpoint: str,
    payload: Dict[str, Any],
    stream: bool = False
) -> Dict[str, Any]:
    """
    Make authenticated request to Perplexity API.

    Args:
        endpoint: API endpoint (e.g., '/chat/completions')
        payload: Request payload
        stream: Whether to use streaming (default: False)

    Returns:
        API response as dictionary

    Raises:
        httpx.HTTPStatusError: For API errors
        httpx.TimeoutException: For timeout errors
    """
    api_key = _get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}{endpoint}",
            headers=headers,
            json=payload,
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()


def _handle_api_error(e: Exception) -> str:
    """
    Format API errors into clear, actionable error messages.

    Args:
        e: Exception that occurred

    Returns:
        Formatted error message string
    """
    if isinstance(e, ValueError):
        return f"Configuration Error: {str(e)}"

    if isinstance(e, httpx.HTTPStatusError):
        status_code = e.response.status_code

        if status_code == 401:
            return "Error: Invalid API key. Please check your PERPLEXITY_API_KEY in the .env file."
        elif status_code == 429:
            return "Error: Rate limit exceeded. Please wait a moment before making more requests."
        elif status_code == 400:
            try:
                error_detail = e.response.json()
                return f"Error: Invalid request - {error_detail.get('error', {}).get('message', 'Bad request')}"
            except:
                return "Error: Invalid request. Please check your parameters."
        elif status_code == 500:
            return "Error: Perplexity API server error. Please try again later."

        return f"Error: API request failed with status {status_code}"

    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. The query may be too complex or the service is slow. Try again."

    return f"Error: Unexpected error occurred: {type(e).__name__} - {str(e)}"


def _truncate_if_needed(content: str, limit: int = CHARACTER_LIMIT) -> str:
    """
    Truncate content if it exceeds character limit.

    Args:
        content: Content to check
        limit: Character limit (default: CHARACTER_LIMIT)

    Returns:
        Original or truncated content with notice
    """
    if len(content) <= limit:
        return content

    truncated = content[:limit]
    truncation_notice = f"\n\n[Response truncated at {limit} characters. Original length: {len(content)} characters]"
    return truncated + truncation_notice


def _format_citations(search_results: Optional[List[Dict[str, Any]]]) -> str:
    """
    Format search result citations into readable markdown.

    Args:
        search_results: List of search result dictionaries from API

    Returns:
        Formatted markdown string with citations
    """
    if not search_results:
        return ""

    citations = ["## Sources\n"]
    for idx, result in enumerate(search_results, 1):
        url = result.get('url', 'N/A')
        title = result.get('title', 'Unknown')
        citations.append(f"{idx}. [{title}]({url})")

    return "\n".join(citations)


# Tool implementations
@mcp.tool(
    name="perplexity_ask",
    annotations={
        "title": "Ask Perplexity AI",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def perplexity_ask(params: PerplexityAskInput) -> str:
    """
    Ask Perplexity AI a question with web search and get an answer with citations.

    This tool uses Perplexity's sonar or sonar-pro models to answer questions by
    searching the web in real-time and synthesizing information from multiple sources.
    It provides up-to-date answers with source citations.

    Args:
        params (PerplexityAskInput): Validated input parameters containing:
            - query (str): Question to ask (e.g., "What are the latest AI developments?")
            - model (PerplexityModel): 'sonar' (fast) or 'sonar-pro' (advanced, default)
            - search_mode (SearchMode): 'web' (default), 'academic', or 'sec'
            - return_citations (bool): Include source citations (default: True)
            - return_images (bool): Include relevant images (default: False)
            - return_related_questions (bool): Suggest follow-up questions (default: False)
            - max_tokens (int): Maximum response length (default: 4096)
            - temperature (float): Randomness 0.0-2.0 (default: 0.2)

    Returns:
        str: Formatted response containing:
            - Answer to the question
            - Citations/sources (if enabled)
            - Related questions (if enabled)
            - Image URLs (if enabled)

    Examples:
        - Use when: "What's the current state of quantum computing?"
        - Use when: "Explain the latest Tesla earnings report"
        - Use when: "Find recent academic papers on climate change"
        - Don't use when: You need deep exhaustive research (use perplexity_research)
        - Don't use when: You need step-by-step reasoning (use perplexity_reason)

    Error Handling:
        - Returns "Configuration Error" if PERPLEXITY_API_KEY not set
        - Returns "Error: Invalid API key" if authentication fails (401)
        - Returns "Error: Rate limit exceeded" if too many requests (429)
        - Returns formatted error message for other failures
    """
    try:
        # Build API payload
        payload = {
            "model": params.model.value,
            "messages": [
                {
                    "role": "user",
                    "content": params.query
                }
            ],
            "max_tokens": params.max_tokens,
            "temperature": params.temperature,
            "search_mode": params.search_mode.value if params.search_mode else "web",
            "return_images": params.return_images,
            "return_related_questions": params.return_related_questions
        }

        # Make API request
        response = await _make_api_request("/chat/completions", payload)

        # Extract response content
        answer = response.get("choices", [{}])[0].get("message", {}).get("content", "No response generated")

        # Build formatted response
        result_parts = [f"# Perplexity AI Response\n\n{answer}\n"]

        # Add citations if available and requested
        if params.return_citations and response.get("search_results"):
            citations = _format_citations(response.get("search_results"))
            if citations:
                result_parts.append(f"\n{citations}\n")

        # Add related questions if available and requested
        if params.return_related_questions and response.get("related_questions"):
            result_parts.append("\n## Related Questions\n")
            for question in response.get("related_questions", []):
                result_parts.append(f"- {question}")
            result_parts.append("")

        # Add image URLs if available and requested
        if params.return_images and response.get("images"):
            result_parts.append("\n## Images\n")
            for img_url in response.get("images", []):
                result_parts.append(f"- {img_url}")
            result_parts.append("")

        # Add usage information
        usage = response.get("usage", {})
        if usage:
            result_parts.append(f"\n---\n**Tokens used**: {usage.get('total_tokens', 'N/A')}")

        result = "\n".join(result_parts)
        return _truncate_if_needed(result)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="perplexity_search",
    annotations={
        "title": "Perplexity Web Search",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def perplexity_search(params: PerplexitySearchInput) -> str:
    """
    Perform focused web search using Perplexity AI with advanced filtering options.

    This tool performs targeted web searches with the ability to filter by recency,
    specific domains, and search modes. It's optimized for finding specific information
    quickly with relevant sources and citations.

    Args:
        params (PerplexitySearchInput): Validated input parameters containing:
            - query (str): Search query (e.g., "latest AI research", "Tesla stock")
            - search_mode (SearchMode): 'web' (default), 'academic', or 'sec'
            - search_recency_filter (str): Time filter - 'day', 'week', 'month', 'year'
            - search_domain_filter (List[str]): Domain allowlist/blocklist (e.g., ['+nytimes.com', '-wikipedia.org'])
            - return_images (bool): Include relevant images (default: True)
            - return_related_questions (bool): Suggest follow-up questions (default: True)

    Returns:
        str: Formatted search results containing:
            - Search results with summaries
            - Source URLs and titles
            - Images (if enabled)
            - Related questions (if enabled)
            - Domain filters applied

    Examples:
        - Use when: "Search for Tesla earnings reports from the past week"
        - Use when: "Find academic papers on quantum computing from 2024"
        - Use when: "Search SEC filings for Apple excluding blog posts"
        - Don't use when: You need comprehensive research (use perplexity_research)
        - Don't use when: You need conversational answers (use perplexity_ask)

    Error Handling:
        - Returns "Configuration Error" if PERPLEXITY_API_KEY not set
        - Returns "Error: Invalid API key" if authentication fails (401)
        - Returns "Error: Rate limit exceeded" if too many requests (429)
        - Validates domain filter has max 20 domains
    """
    try:
        # Build API payload with search parameters
        payload = {
            "model": PerplexityModel.SONAR_PRO.value,  # Use sonar-pro for best search results
            "messages": [
                {
                    "role": "user",
                    "content": params.query
                }
            ],
            "max_tokens": DEFAULT_MAX_TOKENS,
            "temperature": 0.2,  # Lower temperature for factual search results
            "search_mode": params.search_mode.value,
            "return_images": params.return_images,
            "return_related_questions": params.return_related_questions
        }

        # Add optional filters
        if params.search_recency_filter:
            payload["search_recency_filter"] = params.search_recency_filter

        if params.search_domain_filter:
            payload["search_domain_filter"] = params.search_domain_filter

        # Make API request
        response = await _make_api_request("/chat/completions", payload)

        # Extract search results
        answer = response.get("choices", [{}])[0].get("message", {}).get("content", "No results found")

        # Build formatted response
        result_parts = [f"# Search Results: \"{params.query}\"\n"]

        # Add search mode and filters info
        filters_info = [f"**Search Mode**: {params.search_mode.value}"]
        if params.search_recency_filter:
            filters_info.append(f"**Time Filter**: {params.search_recency_filter}")
        if params.search_domain_filter:
            filters_info.append(f"**Domain Filter**: {', '.join(params.search_domain_filter)}")

        result_parts.append("\n".join(filters_info))
        result_parts.append(f"\n## Results\n\n{answer}\n")

        # Add citations
        if response.get("search_results"):
            citations = _format_citations(response.get("search_results"))
            if citations:
                result_parts.append(f"\n{citations}\n")

        # Add related questions
        if params.return_related_questions and response.get("related_questions"):
            result_parts.append("\n## Related Searches\n")
            for question in response.get("related_questions", []):
                result_parts.append(f"- {question}")
            result_parts.append("")

        # Add images
        if params.return_images and response.get("images"):
            result_parts.append("\n## Images\n")
            for img_url in response.get("images", []):
                result_parts.append(f"- {img_url}")
            result_parts.append("")

        result = "\n".join(result_parts)
        return _truncate_if_needed(result)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="perplexity_research",
    annotations={
        "title": "Perplexity Deep Research",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def perplexity_research(params: PerplexityResearchInput) -> str:
    """
    Conduct deep, exhaustive research on a topic using Perplexity's sonar-deep-research model.

    This tool performs comprehensive research by searching multiple sources, analyzing
    information from various perspectives, and synthesizing a detailed report with
    extensive citations. Best for complex topics requiring thorough analysis.

    Args:
        params (PerplexityResearchInput): Validated input parameters containing:
            - research_query (str): Research topic (e.g., "Impact of AI on healthcare 2024-2025")
            - reasoning_effort (ReasoningEffort): Research depth - 'low', 'medium', 'high' (default: 'high')
            - search_mode (SearchMode): Source type - 'web' (default), 'academic', 'sec'
            - return_images (bool): Include visualizations (default: True)

    Returns:
        str: Comprehensive research report containing:
            - Executive summary
            - Detailed analysis from multiple sources
            - Extensive citations
            - Key findings and insights
            - Images and visualizations (if enabled)

    Examples:
        - Use when: "Research the impact of AI on healthcare in 2024-2025"
        - Use when: "Analyze the global semiconductor industry trends"
        - Use when: "Investigate climate change policies across different countries"
        - Don't use when: You need a quick answer (use perplexity_ask)
        - Don't use when: You need targeted search results (use perplexity_search)

    Error Handling:
        - Returns "Configuration Error" if PERPLEXITY_API_KEY not set
        - Returns "Error: Invalid API key" if authentication fails (401)
        - Returns "Error: Rate limit exceeded" if too many requests (429)
        - Validates research query has minimum 10 characters

    Note:
        This tool may take longer to respond due to the comprehensive nature of
        the research. Responses are typically more detailed and citation-rich.
    """
    try:
        # Build API payload for deep research
        payload = {
            "model": PerplexityModel.SONAR_DEEP_RESEARCH.value,
            "messages": [
                {
                    "role": "user",
                    "content": params.research_query
                }
            ],
            "reasoning_effort": params.reasoning_effort.value,
            "search_mode": params.search_mode.value,
            "return_images": params.return_images,
            "return_related_questions": True,  # Always return for research
            "max_tokens": 16384,  # Higher limit for comprehensive research
            "temperature": 0.1  # Low temperature for factual research
        }

        # Make API request (may take longer for deep research)
        response = await _make_api_request("/chat/completions", payload)

        # Extract research content
        research_content = response.get("choices", [{}])[0].get("message", {}).get("content", "No research results generated")

        # Build formatted response
        result_parts = [
            f"# Deep Research Report: {params.research_query}\n",
            f"**Research Depth**: {params.reasoning_effort.value}",
            f"**Source Type**: {params.search_mode.value}\n",
            "---\n",
            research_content,
            "\n"
        ]

        # Add extensive citations
        if response.get("search_results"):
            citations = _format_citations(response.get("search_results"))
            if citations:
                result_parts.append(f"\n{citations}\n")

        # Add related research topics
        if response.get("related_questions"):
            result_parts.append("\n## Related Research Topics\n")
            for question in response.get("related_questions", []):
                result_parts.append(f"- {question}")
            result_parts.append("")

        # Add images/visualizations
        if params.return_images and response.get("images"):
            result_parts.append("\n## Visualizations\n")
            for img_url in response.get("images", []):
                result_parts.append(f"- {img_url}")
            result_parts.append("")

        # Add research metadata
        usage = response.get("usage", {})
        if usage:
            result_parts.append(
                f"\n---\n**Research Metadata**\n"
                f"- Sources consulted: {len(response.get('search_results', []))}\n"
                f"- Tokens used: {usage.get('total_tokens', 'N/A')}"
            )

        result = "\n".join(result_parts)
        return _truncate_if_needed(result)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="perplexity_reason",
    annotations={
        "title": "Perplexity Reasoning",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def perplexity_reason(params: PerplexityReasonInput) -> str:
    """
    Use Perplexity's reasoning models to solve problems and analyze complex situations.

    This tool uses sonar-reasoning or sonar-reasoning-pro models to perform logical
    reasoning, analyze trade-offs, solve problems step-by-step, and provide structured
    analysis. Best for tasks requiring critical thinking and logical deduction.

    Args:
        params (PerplexityReasonInput): Validated input parameters containing:
            - problem (str): Problem or question requiring reasoning (min 10 chars)
            - model (PerplexityModel): 'sonar-reasoning' (fast) or 'sonar-reasoning-pro' (premier, default)
            - temperature (float): Determinism level 0.0 (logical) to 2.0 (creative), default: 0.0

    Returns:
        str: Structured reasoning response containing:
            - Step-by-step analysis
            - Logical deductions
            - Trade-off analysis (if applicable)
            - Conclusion and recommendations

    Examples:
        - Use when: "Analyze pros and cons of remote work for tech companies"
        - Use when: "Compare investment strategies for retirement planning"
        - Use when: "Evaluate different approaches to reducing carbon emissions"
        - Use when: "Solve this logic puzzle: [puzzle description]"
        - Don't use when: You need web search results (use perplexity_search)
        - Don't use when: You need current events info (use perplexity_ask)

    Error Handling:
        - Returns "Configuration Error" if PERPLEXITY_API_KEY not set
        - Returns "Error: Invalid API key" if authentication fails (401)
        - Returns "Error: Rate limit exceeded" if too many requests (429)
        - Validates model is either sonar-reasoning or sonar-reasoning-pro
        - Validates problem has minimum 10 characters

    Note:
        This tool does NOT perform web searches. It uses reasoning capabilities
        based on the model's training data. For current information, use perplexity_ask.
    """
    try:
        # Build API payload for reasoning
        payload = {
            "model": params.model.value,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert reasoning engine. Analyze problems step-by-step, consider multiple perspectives, and provide clear logical deductions."
                },
                {
                    "role": "user",
                    "content": params.problem
                }
            ],
            "temperature": params.temperature,
            "max_tokens": 8192,  # Higher limit for detailed reasoning
            "disable_search": True  # Disable web search for pure reasoning
        }

        # Make API request
        response = await _make_api_request("/chat/completions", payload)

        # Extract reasoning content
        reasoning_content = response.get("choices", [{}])[0].get("message", {}).get("content", "No reasoning response generated")

        # Build formatted response
        result_parts = [
            f"# Reasoning Analysis\n",
            f"**Model**: {params.model.value}",
            f"**Temperature**: {params.temperature} (0.0 = most logical, 2.0 = most creative)\n",
            "---\n",
            reasoning_content,
            "\n"
        ]

        # Add usage information
        usage = response.get("usage", {})
        if usage:
            result_parts.append(
                f"\n---\n**Analysis Metadata**\n"
                f"- Tokens used: {usage.get('total_tokens', 'N/A')}\n"
                f"- Mode: Pure reasoning (web search disabled)"
            )

        result = "\n".join(result_parts)
        return _truncate_if_needed(result)

    except Exception as e:
        return _handle_api_error(e)


if __name__ == "__main__":
    mcp.run()
