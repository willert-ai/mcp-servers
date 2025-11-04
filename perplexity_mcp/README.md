# Perplexity MCP Server

MCP server for Perplexity AI, providing access to advanced AI search, research, and reasoning capabilities using the latest Perplexity models.

## Features

This server provides 4 comprehensive tools for interacting with Perplexity AI:

### 1. **perplexity_ask** - General Q&A with Citations
- Ask questions and get answers with real-time web search
- Uses sonar or sonar-pro models
- Includes source citations and optional images
- Configurable search modes: web, academic, SEC filings

### 2. **perplexity_search** - Advanced Web Search
- Focused search with filtering options
- Filter by recency (day, week, month, year)
- Filter by domains (allowlist/blocklist up to 20 domains)
- Returns structured results with citations

### 3. **perplexity_research** - Deep Research
- Comprehensive research using sonar-deep-research model
- Configurable reasoning effort (low, medium, high)
- Extensive citations from multiple sources
- Best for complex topics requiring thorough analysis

### 4. **perplexity_reason** - Logical Reasoning
- Step-by-step problem solving and analysis
- Uses sonar-reasoning or sonar-reasoning-pro models
- Trade-off analysis and logical deductions
- Pure reasoning without web search

## Available Models

- **sonar**: Lightweight, fast responses
- **sonar-pro**: Advanced search with better quality
- **sonar-deep-research**: Exhaustive research with extensive sources
- **sonar-reasoning**: Fast logical reasoning
- **sonar-reasoning-pro**: Premier reasoning capabilities

## Configuration

### Required Environment Variables

Add to `.env` file:
```bash
PERPLEXITY_API_KEY=your_api_key_here
```

### Get API Key

1. Sign up at [Perplexity AI](https://www.perplexity.ai/)
2. Go to API settings: https://www.perplexity.ai/settings/api
3. Generate a new API key
4. Add it to your `.env` file

## Installation

```bash
# Install dependencies
cd /Users/aiveo/mcp-servers/perplexity_mcp
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 -m pip install -r requirements.txt

# Add to Claude Code
claude mcp add perplexity-mcp \
  --type stdio \
  --command /Users/aiveo/.pyenv/versions/3.11.9/bin/python3 \
  --arg /Users/aiveo/mcp-servers/perplexity_mcp/server.py

# Verify
claude mcp list
```

## Usage Examples

### Ask a Question
```
"Use Perplexity to explain the latest developments in quantum computing"
"What are the recent AI breakthroughs in 2025?"
"Find information about Tesla's latest earnings report"
```

### Search with Filters
```
"Search Perplexity for AI research papers from the past week"
"Find recent SEC filings for Apple"
"Search for climate change articles, excluding Wikipedia"
```

### Deep Research
```
"Research the impact of AI on healthcare in 2024-2025"
"Conduct deep research on renewable energy trends"
"Analyze the global semiconductor industry comprehensively"
```

### Logical Reasoning
```
"Analyze the pros and cons of remote work for tech companies"
"Compare different investment strategies for retirement"
"Evaluate approaches to reducing carbon emissions"
```

## Tools Reference

| Tool | Description | Best For |
|------|-------------|----------|
| `perplexity_ask` | Q&A with citations | Quick questions, current events |
| `perplexity_search` | Advanced search | Finding specific information |
| `perplexity_research` | Deep research | Comprehensive analysis |
| `perplexity_reason` | Logical reasoning | Problem-solving, analysis |

## Features by Tool

### perplexity_ask
- ✅ Real-time web search
- ✅ Multiple search modes (web, academic, SEC)
- ✅ Source citations
- ✅ Optional images
- ✅ Related questions
- ✅ Configurable temperature

### perplexity_search
- ✅ Recency filtering
- ✅ Domain filtering (up to 20 domains)
- ✅ Search mode selection
- ✅ Images in results
- ✅ Related searches

### perplexity_research
- ✅ Exhaustive multi-source analysis
- ✅ Configurable research depth
- ✅ Extensive citations
- ✅ Higher token limits (16K)
- ✅ Visualizations

### perplexity_reason
- ✅ Step-by-step analysis
- ✅ Trade-off evaluation
- ✅ Logic-based reasoning
- ✅ No web search (pure reasoning)
- ✅ Configurable determinism

## API Endpoint

All tools use the Perplexity Chat Completions API:
```
https://api.perplexity.ai/chat/completions
```

## Rate Limits

- Standard plan: Check your Perplexity plan for rate limits
- Pro plan: Higher rate limits available
- Errors return clear messages with retry guidance

## Error Handling

The server provides clear, actionable error messages:
- `Configuration Error`: API key not set in .env
- `Invalid API key`: Authentication failed
- `Rate limit exceeded`: Too many requests
- `Request timed out`: Query too complex or service slow

## Character Limits

Responses are limited to 25,000 characters with graceful truncation and clear notices when limits are reached.

## Security

- API key stored in `.env` file (gitignored)
- No hardcoded credentials
- Secure HTTPS communication
- Input validation with Pydantic models

## Troubleshooting

### "Configuration Error: PERPLEXITY_API_KEY not set"
```bash
# Verify .env file exists
cat /Users/aiveo/mcp-servers/perplexity_mcp/.env

# Should contain:
PERPLEXITY_API_KEY=your_key_here
```

### "Error: Invalid API key"
- Verify your API key is correct
- Check it hasn't expired
- Ensure no extra spaces or quotes

### "Error: Rate limit exceeded"
- Wait a moment before making more requests
- Consider upgrading your Perplexity plan
- Use caching for repeated queries

### Test server manually
```bash
cd /Users/aiveo/mcp-servers/perplexity_mcp
/Users/aiveo/.pyenv/versions/3.11.9/bin/python3 server.py
# Should wait for stdin (Ctrl+C to exit)
```

## Resources

- [Perplexity AI](https://www.perplexity.ai/)
- [Perplexity API Docs](https://docs.perplexity.ai/)
- [API Reference](https://docs.perplexity.ai/reference/post_chat_completions)
- [MCP Protocol](https://modelcontextprotocol.io/)

## Version

- **Server Version**: 1.0.0
- **API Version**: v1 (2025)
- **MCP Protocol**: Latest
- **Created**: 2025-11-04
