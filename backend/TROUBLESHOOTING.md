# 🧠 CSO.ai - Troubleshooting Guide

Common issues and solutions for CSO.ai.

---

## Installation Issues

### "Module not found: cso_ai"

**Problem**: Package not installed or wrong Python environment.

**Solution**:
```bash
cd cso-ai
uv venv && uv pip install -e .
```

Verify installation:
```bash
python -c "import cso_ai; print('OK')"
```

### "README.md not found" during install

**Problem**: Missing README.md file.

**Solution**:
```bash
cp README_REFINED.md README.md
uv pip install -e .
```

---

## MCP Server Issues

### Server not appearing in Cursor

**Problem**: MCP configuration not loaded.

**Solution**:

1. Check `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "cso-ai": {
      "command": "/path/to/cso-ai/.venv/bin/python",
      "args": ["-m", "cso_ai.server"]
    }
  }
}
```

2. Restart Cursor completely (Cmd+Q, then reopen)

3. Check server logs in Cursor's MCP panel

### "Connection refused" or server crashes

**Problem**: Python environment or dependency issues.

**Solution**:

1. Test server manually:
```bash
cd cso-ai
source .venv/bin/activate
python -m cso_ai.server
```

2. Check for errors in output

3. Reinstall dependencies:
```bash
uv pip install -e . --force-reinstall
```

---

## Tool Errors

### "Request Timed Out"

**Problem**: Network slow or external services down.

**Solutions**:
- Check internet connection
- Try again in a few moments
- External services (HN, Lobsters, GitHub) may be temporarily unavailable

### "Network Error"

**Problem**: Cannot connect to external services.

**Solutions**:
- Verify internet connection
- Check firewall/proxy settings
- Some corporate networks block external APIs

### "Rate Limited"

**Problem**: Too many requests to external services.

**Solutions**:
- Wait a few minutes before trying again
- Use cached results (they're valid for 1 hour)
- Reduce query frequency

### "Service Unavailable" (HTTP 500+)

**Problem**: External service is down.

**Solutions**:
- Wait and try again later
- Check service status:
  - Hacker News: https://news.ycombinator.com
  - Lobsters: https://lobste.rs
  - GitHub: https://www.githubstatus.com

---

## LLM/Groq Issues

### No GROQ_API_KEY set

**Problem**: Smart article scoring unavailable.

**Impact**: Falls back to heuristic scoring (less accurate).

**Solution**:

1. Get free API key: https://console.groq.com/keys

2. Add to `.env`:
```bash
# In cso-ai/.env
GROQ_API_KEY=your_key_here
```

3. Restart MCP server

### "Groq API error"

**Problem**: API key invalid or quota exceeded.

**Solutions**:
- Verify API key is correct
- Check Groq console for quota/limits
- System will fall back to heuristic scoring

---

## Performance Issues

### "Queries are slow (> 3 seconds)"

**Problem**: Cache not working or first query.

**Diagnosis**:
- First query: ~2-3s (normal - fetching + scoring)
- Subsequent queries: < 1s (should be cached)

**Solutions**:

1. Check cache status in output:
```
⚡ Analyzed in 0.8s | From cache  ← Good!
⚡ Analyzed in 2.5s | Next refresh in 60 min  ← First query
```

2. If always slow, check database:
```bash
ls -lh ~/.cso-ai/data.db
# Should exist and grow over time
```

3. Clear cache if corrupted:
```bash
rm ~/.cso-ai/data.db
# Will rebuild on next query
```

### "High memory usage"

**Problem**: Large cache or many profiles.

**Solutions**:
- Clear old data:
```bash
rm ~/.cso-ai/data.db
```

- Cache is designed to be lightweight (< 10MB typical)

---

## Data/Cache Issues

### "No articles found"

**Problem**: Cache empty or fetch failed.

**Solutions**:

1. Force refresh:
```
"What should I read?" with refresh: true
```

2. Check network connectivity

3. Verify sources are accessible:
```bash
curl https://hacker-news.firebaseio.com/v0/topstories.json
curl https://lobste.rs/rss
curl https://github.com/trending
```

### "Articles not relevant to my stack"

**Problem**: Profile not detected correctly.

**Solutions**:

1. Check detected stack in output:
```
📰 Top Articles for Your Stack (Python + FastAPI + React)
                                 ^^^^^^^^^^^^^^^^^^^^^^^^
```

2. If wrong, ensure you're in the right directory:
```bash
pwd  # Should be your project directory
```

3. Profile is cached for 24 hours - wait or clear cache:
```bash
rm ~/.cso-ai/data.db
```

### "Scores seem wrong"

**Problem**: LLM scoring issue or cache from different profile.

**Solutions**:

1. Check if GROQ_API_KEY is set (better scoring)

2. Scores are cached per profile - if you changed your stack significantly, clear cache:
```bash
rm ~/.cso-ai/data.db
```

---

## Test Failures

### "Tests fail with import errors"

**Problem**: Package not installed in test environment.

**Solution**:
```bash
source .venv/bin/activate
uv pip install -e .
python -m pytest tests/ -v
```

### "Async tests fail"

**Problem**: pytest-asyncio not installed or configured.

**Solution**:
```bash
uv pip install pytest-asyncio
```

Verify `pyproject.toml` has:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

---

## Common Questions

### Q: How often does the cache refresh?

**A**: Articles are cached for 1 hour. Scores are cached forever (per article + profile combo).

### Q: Can I use CSO.ai offline?

**A**: Partially. Cached articles work offline, but fetching new articles requires internet.

### Q: How much does Groq API cost?

**A**: Groq has a generous free tier. CSO.ai caches scores aggressively to minimize API calls.

### Q: Can I add custom RSS sources?

**A**: Not yet, but it's on the roadmap (v1.1).

### Q: Where is data stored?

**A**: `~/.cso-ai/data.db` (SQLite database, safe to delete if needed).

---

## Getting Help

If you're still stuck:

1. **Check logs**: Look for errors in Cursor's MCP panel

2. **Run tests**: `python -m pytest tests/ -v` to verify installation

3. **Manual test**:
```bash
cd cso-ai
source .venv/bin/activate
python -c "
from cso_ai.intel.auto_intelligence import AutoIntelligence
import asyncio

async def test():
    ai = AutoIntelligence()
    profile = await ai.get_or_create_profile('.')
    print(f'Detected: {profile.primary_language}')

asyncio.run(test())
"
```

4. **File an issue**: Include error messages and steps to reproduce

---

## Debug Mode

Enable debug logging:

```bash
# In your shell before starting Cursor
export CSO_AI_DEBUG=1
```

This will show detailed logs for troubleshooting.
