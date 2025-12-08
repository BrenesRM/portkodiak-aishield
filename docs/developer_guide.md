# Developer Guide

## Getting Started

### Prerequisites

- Windows 10/11 or Windows Server 2016+
- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Visual Studio Build Tools (for C extensions)
- Windows SDK (for WFP development)

### Initial Setup

1. **Install uv package manager**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. **Clone and setup repository**
```bash
git clone https://github.com/yourusername/portkodiak-aishield.git
cd portkodiak-aishield
uv sync
```

3. **Install pre-commit hooks**
```bash
uv run pre-commit install
```

4. **Run development environment**
```bash
uv run dev
```

## Project Structure

See [Architecture](architecture.md) for detailed component descriptions.

## Development Workflow

### Running Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest tests/unit

# With coverage
uv run pytest --cov

# Specific test file
uv run pytest tests/unit/test_policy_engine.py
```

### Code Quality

```bash
# Linting
uv run ruff check .
uv run ruff check . --fix  # Auto-fix

# Formatting
uv run black .

# Type checking
uv run mypy app/
```

### Building

```bash
# Build installer
uv run scripts/build.py

# Sign code
uv run scripts/sign_code.ps1
```

## Coding Standards

- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for all public APIs
- Maintain test coverage > 80%
- All commits must pass pre-commit hooks

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Make changes with tests
4. Run code quality checks
5. Submit pull request

## Common Issues

### WFP Integration
- Requires administrator privileges
- May conflict with other firewalls
- Test in VM first

### ML Models
- ONNX export can be tricky
- Test inference before deployment
- Monitor memory usage

## Resources

- [Windows Filtering Platform](https://docs.microsoft.com/en-us/windows/win32/fwp/windows-filtering-platform-start-page)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Portmaster Reference](https://github.com/safing/portmaster)
