#!/usr/bin/env python3
"""
Minimal Perplexity MCP Server for Debugging
"""

from fastmcp import FastMCP
from dotenv import load_dotenv
import os
import httpx
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Get API key
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not PERPLEXITY_API_KEY:
    raise ValueError("PERPLEXITY_API_KEY not set in .env file")

# Initialize MCP server
mcp = FastMCP("perplexity-mcp")

# Perplexity API configuration
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


class AskInput(BaseModel):
    """Input for asking Perplexity a question"""
    query: str = Field(..., description="The question to ask")


@mcp.tool()
async def perplexity_ask(query: str) -> str:
    """
    Ask Perplexity AI a simple question.

    Args:
        query: The question to ask

    Returns:
        Answer from Perplexity AI
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                PERPLEXITY_API_URL,
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "user", "content": query}
                    ]
                }
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
                return answer
            else:
                return f"Error: API returned status {response.status_code}"

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
