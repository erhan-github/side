# Contributing to Side

Thank you for your interest in contributing to Side! This guide will help you get started.

---

## 🚀 Quick Start

### 1. Fork & Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/erhan-github/side.git
cd side/backend
```

### 2. Set Up Development Environment

```bash
# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### 3. Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=side --cov-report=html

# Specific test file
pytest tests/test_auto_intelligence.py -v
```

### 4. Make Your Changes

```bash
# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes
# ... edit files ...

# Run tests
pytest tests/ -v

# Lint & format
ruff check src/
ruff format src/
```

### 5. Submit a Pull Request

```bash
# Commit your changes
git add .
git commit -m "Add amazing feature"

# Push to your fork
git push origin feature/amazing-feature

# Open a PR on GitHub
```

---

## 📋 Development Guidelines

### Code Style

We use **Ruff** for linting and formatting:

```bash
# Check for issues
ruff check src/

# Auto-fix issues
ruff check src/ --fix

# Format code
ruff format src/
```

**Key Principles**:
- **PEP 8** compliance
- **Type hints** for all functions
- **Docstrings** for public APIs
- **Comments** explain why, not what

### Testing

**All new features must include tests.**

```python
# Example test structure
import pytest
from side.your_module import your_function

class TestYourFeature:
    """Tests for your amazing feature."""

    def test_basic_functionality(self):
        """Test basic use case."""
        result = your_function("input")
        assert result == "expected"

    def test_edge_case(self):
        """Test edge case handling."""
        with pytest.raises(ValueError):
            your_function(None)

    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test async functionality."""
        result = await your_async_function()
        assert result is not None
```

**Test Coverage**:
- Aim for **> 80% coverage**
- Test happy paths AND edge cases
- Include integration tests for new features

### Commit Messages

Use **conventional commits**:

```
feat: add morning briefing feature
fix: resolve cache invalidation bug
docs: update API documentation
test: add tests for context tracker
refactor: simplify retry logic
perf: optimize database queries
```

**Format**:
- **Type**: feat, fix, docs, test, refactor, perf, chore
- **Scope** (optional): module or feature
- **Description**: imperative, lowercase, no period

---

## 🏗️ Project Structure

```
side/
├── src/side/             # Source code
│   ├── server.py         # MCP server entry point
│   ├── tools/            # Modular tool definitions
│   ├── intel/            # Intelligence modules (Forensics, Scoring)
│   ├── storage/          # Database layer (SQLite)
│   ├── services/         # Background services (Monolith, Watchers)
│   ├── sources/          # Data sources (RSS, Git)
│   └── utils/            # Utilities
├── tests/                # Test suite
├── docs/                 # Documentation
└── pyproject.toml        # Project config
```

### Key Modules

**Core**:
- `tools/`: Modular tool implementations (audit, planning, strategy)
- `server.py`: MCP server implementation

**Intelligence**:
- `intel/forensic_engine.py`: AST-based code forensics & deployment checks
- `intel/intelligence_store.py`: Central finding persistence
- `intel/strategist.py`: LLM-powered strategic reasoning
- `intel/auto_intelligence.py`: Zero-setup stack detection

**Storage**:
- `storage/simple_db.py`: Local SQLite database (Profile, Activities, Findings)

**Services**:
- `services/monolith.py`: Generates the `.side/MONOLITH.md` dashboard
- `services/file_watcher.py`: File change monitoring

---

## 🎯 Areas for Contribution

### High Priority

1. **New Article Sources**
   - Reddit (r/programming, r/python, etc.)
   - Dev.to
   - Medium publications
   - Custom RSS feeds

2. **Team Features**
   - Shared knowledge base
   - Collaborative filtering
   - Team analytics

3. **Performance Optimization**
   - Faster article fetching
   - Better caching strategies
   - Database query optimization

### Medium Priority

4. **UI/UX Improvements**
   - Better formatting
   - Rich media support
   - Interactive elements

5. **Integrations**
   - Slack notifications
   - Discord bot
   - Browser extension

6. **Analytics**
   - Usage tracking
   - Recommendation quality metrics
   - A/B testing framework

### Low Priority

7. **Documentation**
   - More examples
   - Video tutorials
   - Blog posts

8. **Testing**
   - Increase coverage
   - Performance benchmarks
   - Load testing

---

## 🐛 Reporting Bugs

**Before submitting**:
1. Check [existing issues](https://github.com/erhan-github/side/issues)
2. Try latest version
3. Gather debug info

**Bug Report Template**:

```markdown
### Description
Clear description of the bug

### Steps to Reproduce
1. Step one
2. Step two
3. ...

### Expected Behavior
What should happen

### Actual Behavior
What actually happens

### Environment
- OS: macOS 14.0
- Python: 3.11.6
- Side version: 0.1.0
- Cursor version: 0.40.0

### Debug Info
```bash
export SIDE_AI_DEBUG=1
# Run command that triggers bug
# Paste output here
```

### Additional Context
Any other relevant information
```

---

## 💡 Feature Requests

**Before submitting**:
1. Check [roadmap](docs/ROADMAP.md)
2. Search existing issues
3. Consider if it fits Sidelith's philosophy

**Feature Request Template**:

```markdown
### Problem
What problem does this solve?

### Proposed Solution
How should it work?

### Alternatives Considered
What other approaches did you consider?

### Additional Context
Mockups, examples, etc.
```

---

## 🔍 Code Review Process

All PRs go through code review:

**Checklist**:
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Linting passes (`ruff check src/`)
- [ ] Code is formatted (`ruff format src/`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] No breaking changes (or clearly documented)

**Review Focus**:
- **Correctness**: Does it work as intended?
- **Performance**: Any performance implications?
- **Maintainability**: Is it easy to understand?
- **Testing**: Adequate test coverage?
- **Documentation**: Clear docstrings & comments?

**Timeline**:
- Initial review: Within 48 hours
- Follow-up: Within 24 hours
- Merge: After approval + CI passes

---

## 🎨 Design Principles

When contributing, keep these principles in mind:

### 1. **Zero Setup**
- Auto-detect everything possible
- No configuration required
- Works out of the box

### 2. **Instant Value**
- First query delivers value
- < 1 second for cached responses
- Beautiful, scannable output

### 3. **Production Quality**
- Comprehensive error handling
- Retry logic for network calls
- Graceful degradation

### 4. **Developer-First**
- Conversational, not robotic
- Contextual, not generic
- Actionable, not informational

### 5. **Privacy-Focused**
- Local-first architecture
- No data leaves machine (except API calls)
- User has full control

---

## 📚 Resources

- **[Architecture](docs/ARCHITECTURE.md)**: System design
- **[API Reference](docs/API.md)**: Tool specifications
- **[Roadmap](docs/ROADMAP.md)**: Future plans
- **[Troubleshooting](../TROUBLESHOOTING.md)**: Common issues

---

## 🙏 Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Invited to contributor Discord (coming soon)

---

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 💬 Questions?

- **GitHub Discussions**: Ask questions, share ideas
- **Issues**: Bug reports, feature requests
- Twitter: [@sidemcp](https://twitter.com/sidemcp)

---

**Thank you for making Side better!** 🚀
