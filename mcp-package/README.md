# @side-ai/mcp

> The Strategic Partner that thinks for you.

**Side** is a strategic intelligence layer for your IDE. It runs a virtual Boardroom of AI experts that review every line of code.

## Quick Start

### 1. Get Your API Key
Visit [sidelith.com](https://sidelith.com) and sign in with GitHub. Your API key is generated instantly.

### 2. Add to Cursor
Add this to your Cursor MCP settings (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "side": {
      "command": "npx",
      "args": ["-y", "@side-ai/mcp"],
      "env": {
        "SIDE_API_KEY": "sk_your_api_key_here"
      }
    }
  }
}
```

### 3. Start Using Side
In Cursor, just chat with Side:

- `"side audit"` - Run full code review
- `"side plan"` - Set and track goals
- `"side simulate"` - Test with virtual users

## Features

| Feature | Description |
|---------|-------------|
| **The Boardroom** | 8 AI experts review your code |
| **Project Memory** | Remembers your decisions and goals |
| **Progress Tracking** | See how your code health improves |
| **Virtual Users** | Test ideas with simulated personas |

## Requirements

- Node.js 18+
- Python 3.11+ (for the MCP server)
- `pip install side-ai`

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SIDE_API_KEY` | Your Side API key (required) |
| `SIDE_PYTHON` | Path to Python (default: `python3`) |

## Links

- [Website](https://sidelith.com)
- [Documentation](https://docs.sidelith.com)
- [GitHub](https://github.com/erhan-github/side)

## License

MIT
