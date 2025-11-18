# Copilot Instructions for Broadcast

## Project Overview

Python client library for the AEBroadcast API - a financial data service for Brazilian stock market quotes. Single-class design (`Broadcast`) with automatic session management and token refresh.

## Architecture & Key Patterns

### Stateful Session Management
The `Broadcast` class maintains authentication state through its lifecycle:
- **Auto-login on `__init__`**: Constructor calls `login()` and stores tokens immediately
- **Token storage**: Both `token` and `refreshToken` (with `refresh_token` snake_case alias)
- **Property pattern**: `refreshToken` property provides backward-compatible camelCase access
- **Bearer auth**: All authenticated endpoints inject `authorization` header dynamically

Example from `datafeed.py`:
```python
def __init__(self, usr: str, pwd: str, keep_alive: bool = False, verify_ssl: bool = True):
    self.client = httpx.Client(headers=self.headers, timeout=None, verify=verify_ssl)
    self.tokens: dict[str, Any] = self.login(usr, pwd)  # Auto-login
    self.token: str = self.tokens["token"]
```

### Error Handling Contract
All API methods follow a consistent exception pattern:
- Raise `httpx.RequestError` for connection/SSL failures
- Raise `httpx.HTTPStatusError` for HTTP errors (use `response.raise_for_status()`)
- Print error details before re-raising (helps debugging but may need review for production)
- `token_refresh()` is the exception - returns `False` on error instead of raising

### HTTP Client Architecture
- Single `httpx.Client` instance stored in `self.client`
- Base headers in `self.headers` (accept + content-type)
- Auth header injected per-request: `self.client.headers["authorization"] = f"Bearer {self.token}"`
- Configurable SSL verification via `verify_ssl` parameter (defaults to `True`)

## Development Workflow

### Setup Commands
```bash
# Install uv package manager
pip install uv

# Sync exact dependencies from lock file (CRITICAL: always use --locked)
uv sync --locked --all-extras --dev
```

### Test Environment Setup
Create `.env.test` file in project root for test credentials (optional):
```bash
BROADCAST_TEST_USER=your_test_username
BROADCAST_TEST_PASSWORD=your_test_password
```
Tests use these environment variables via `pytest_configure` hook that loads dotenv. If not provided, defaults to `"test_user"` and `"test_password"`.

### Testing Commands
```bash
# Run with coverage (matches CI configuration - target: 98%)
uv run pytest --cov --cov=broadcast --cov-report=xml

# Verbose output for specific test
uv run pytest tests/test_datafeed.py::TestBroadcast::test_get_quote_success -v
```

### Linting
```bash
# Check only
uv run ruff check .

# Auto-fix safe issues
uv run ruff check . --fix
```

## Testing Patterns (Critical for New Tests)

### Mock Setup Pattern
From `test_datafeed.py`:
```python
@pytest.fixture
def mock_httpx_client():
    with patch("httpx.Client") as mock_client:
        client_instance = MagicMock()
        client_instance.headers = {}  # Real dict, not mock
        mock_client.return_value = client_instance
        
        # Setup default login response
        login_response = MagicMock()
        login_response.json.return_value = {"token": "fake_token", "refreshToken": "fake_refresh_token"}
        client_instance.post.return_value = login_response
        
        yield client_instance
```

### Multi-step Test Pattern
When testing after `__init__` (which calls `post` for login):
```python
broadcast = Broadcast("test_user", "test_password")  # Consumes one post call
mock_httpx_client.post.reset_mock()  # Reset before testing your method
mock_httpx_client.post.return_value = your_test_response
result = broadcast.your_method()  # Now assertions are clean
```

## Code Style Conventions (PEP 8 + Clean Code)

### Language Requirements
- **ALL code in English**: Variables, functions, classes, docstrings, comments (PEP 8 requirement for public repos)
- **No Portuguese**: Even for domain-specific terms - use English equivalents
- **Examples**: Use `user` not `usuario`, `password` not `senha`, `quote` not `cotacao`

### Type Annotations
- **All function signatures**: Parameters and return types must have hints
- **Modern syntax**: Use `dict[str, Any]` not `Dict[str, Any]` (Python 3.14+)
- **Union syntax**: Use `dict[str, Any] | bool` not `Union[dict, bool]`

### Docstrings (Google Style)
Required sections: Args, Returns, Raises, Examples. Example from codebase:
```python
def get_quote(self, symbols: list[str], fields: list[str] | None = None) -> dict[str, Any]:
    """
    Retrieve quotes for the requested financial instruments.

    Args:
        symbols (list[str]): List of instrument symbols (e.g., ["PETR4", "VALE3"]).
        fields (list[str], optional): List of desired fields. Default: None.

    Returns:
        dict[str, Any]: Quote payload or error message.

    Raises:
        httpx.RequestError: Connection or SSL error.
        httpx.HTTPStatusError: HTTP error returned by the API.

    Examples:
        >>> client = Broadcast("username", "password")
        >>> quotes = client.get_quote(["PETR4", "VALE3"])
    """
```

### Naming Conventions (PEP 8)
- **Variables/functions**: `snake_case` (e.g., `refresh_token`, `get_quote`)
- **Classes**: `PascalCase` (e.g., `Broadcast`, `TestBroadcast`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
- **Private**: Single underscore prefix (e.g., `_internal_method`)
- **Magic methods**: Double underscore (e.g., `__init__`, `__all__`)

### File Headers
Include at top of all `.py` files:
```python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
```

## CI/CD Configuration

GitHub Actions workflow (`.github/workflows/python-uv-build.yml`):
- Triggers: Push/PR to `main` or `develop` branches
- Python version: Read from `.python-version` file (currently 3.14)
- Coverage upload: Codecov with `unittests` flag
- Critical step: `uv sync --locked --all-extras --dev` (never install packages manually)

## Common Pitfalls

1. **Lock file drift**: Never run `uv add` or `uv sync` without `--locked` in CI
2. **Test pollution**: Always `reset_mock()` after `__init__` in tests (login consumes mock)
3. **SSL in dev**: Use `verify_ssl=False` only for local testing, never commit defaults
4. **Mutable defaults**: `fields: list[str] | None = None` pattern (check for `[]` inside function)
5. **Property aliases**: Remember `refreshToken` property when accessing - both work
6. **Language mixing**: Never mix Portuguese/English in code - stick to English per PEP 8

## Package Structure

- **`src/broadcast/__init__.py`**: Exports only `Broadcast` class
- **`src/broadcast/py.typed`**: PEP 561 marker for type checking support
- **`tests/test_datafeed.py`**: Single comprehensive test file (~412 lines, 98% coverage)
- **`pyproject.toml`**: Uses `hatchling` build backend, dependencies in `[project]` and `[dependency-groups]`
