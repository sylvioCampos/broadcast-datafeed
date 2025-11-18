# Copilot Instructions for Broadcast

## Project Overview

This is a Python client library for interacting with the AEBroadcast API service. It provides authentication and methods to retrieve financial data, such as stock quotes, from the AEBroadcast platform.

## Technology Stack

- **Python Version**: 3.14+ (see `.python-version`)
- **Package Manager**: `uv` (modern Python package manager)
- **HTTP Client**: `httpx` for making API requests
- **Testing**: `pytest` with `pytest-cov` for coverage
- **Linting**: `ruff` for code quality checks
- **Type Checking**: Python type hints are used throughout

## Project Structure

```
src/broadcast/     # Main source code
  __init__.py      # Package exports
  datafeed.py      # Core Broadcast client class
  py.typed         # PEP 561 marker for type hints
tests/             # Test suite
  test_datafeeder.py  # Unit tests for Broadcast class
```

## Development Workflow

### Setting Up the Environment

```bash
# Install uv if not already installed
pip install uv

# Sync dependencies (installs from uv.lock)
uv sync --locked --all-extras --dev
```

### Running Tests

```bash
# Run all tests with coverage
uv run pytest --cov --cov=broadcast --cov-report=xml

# Run specific test file
uv run pytest tests/test_datafeeder.py -v
```

### Linting

```bash
# Check code with ruff
uv run ruff check .

# Auto-fix issues where possible
uv run ruff check . --fix
```

## Code Style Guidelines

1. **Type Hints**: Always use type hints for function arguments and return values
2. **Docstrings**: Use Google-style docstrings with Args, Returns, Raises sections
3. **Error Handling**: Use specific exception types (httpx.RequestError, httpx.HTTPStatusError)
4. **Variable Naming**: Use descriptive names with type annotations
5. **Language**: Code comments and docstrings can be in Portuguese (project's natural language)

## API Client Patterns

When working with the Broadcast client:

1. **Authentication**: The client automatically handles login on initialization
2. **Token Management**: Tokens are stored as instance attributes (`token`, `refreshToken`)
3. **HTTP Headers**: Headers are managed centrally in `self.headers`
4. **Error Handling**: All API methods should handle `httpx.RequestError` and `httpx.HTTPStatusError`
5. **SSL**: The client currently uses `verify=False` for SSL (be aware of security implications)

## Testing Patterns

- Use `pytest.fixture` for mock setup (see `mock_httpx_client` fixture)
- Mock `httpx.Client` at the module level
- Reset mocks between test steps when testing multiple API calls
- Test both success and error scenarios
- Use `pytest.raises` for exception testing

## Dependencies

### Runtime Dependencies
- `httpx>=0.28.1` - HTTP client for API requests

### Development Dependencies
- `pytest>=8.3.5` - Testing framework
- `pytest-cov>=6.1.1` - Code coverage
- `pytest-env>=1.1.5` - Environment variable management for tests
- `pytest-mock>=3.14.0` - Mocking utilities
- `python-dotenv>=1.1.0` - Environment variable loading
- `ruff>=0.11.10` - Linting and formatting

## Important Notes

1. **Lock File**: Always use `uv sync --locked` to respect `uv.lock`
2. **Python Version**: Requires Python 3.14+ (very modern!)
3. **CI/CD**: GitHub Actions workflow runs on `main` and `develop` branches
4. **Coverage**: Project aims for high test coverage (currently ~94%)
5. **License**: MIT License

## When Making Changes

1. Run tests before and after changes: `uv run pytest`
2. Check code quality: `uv run ruff check .`
3. Ensure type hints are present for new functions
4. Update tests if modifying API client behavior
5. Keep dependencies locked - only update when necessary
6. Respect existing code style and patterns
