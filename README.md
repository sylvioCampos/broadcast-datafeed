[![Build Status](https://github.com/sylvioCampos/broadcast/actions/workflows/python-uv-build.yml/badge.svg)](https://github.com/sylvioCampos/broadcast/actions)
[![Coverage Status](https://codecov.io/gh/sylvioCampos/broadcast/branch/main/graph/badge.svg)](https://codecov.io/gh/sylvioCampos/broadcast)
[![Last Commit](https://img.shields.io/github/last-commit/sylvioCampos/broadcast.svg)](https://github.com/sylvioCampos/broadcast/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/downloads/)

# Broadcast

A Python client for interacting with the AEBroadcast API service.  
This package provides authentication and methods to retrieve financial data, such as stock quotes, from the AEBroadcast platform.

## 📋 Features

- 🔐 Simple authentication with the AEBroadcast API
- 📊 Stock quotes and financial data retrieval
- 🔄 Automatic authentication token management
- ⚡ Async HTTP client with `httpx`
- 🛡️ Robust exception handling
- ✅ 98% test coverage

## 🚀 Installation

### Via pip (PyPI)

```bash
pip install broadcast
```

### Via Git

```bash
pip install git+https://github.com/sylvioCampos/broadcast.git
```

### For Development

```bash
git clone https://github.com/sylvioCampos/broadcast.git
cd broadcast
uv sync --locked --all-extras --dev
```

## 📖 Usage

### Basic Example

```python
from broadcast import Broadcast

# Initialize the client
client = Broadcast("your_username", "your_password")

# Get quotes for a list of symbols
quotes = client.get_quote(["PETR4", "VALE3"])
print(quotes)

# Logout when done
client.logout()
```

### Advanced Examples

#### Keeping Session Alive

```python
# Initialize with keep_alive to keep the session active
client = Broadcast("your_username", "your_password", keep_alive=True)

# Session will be kept alive automatically
quotes = client.get_quote(["BBAS3", "ITUB4"])
```

#### Specifying Specific Fields

```python
client = Broadcast("your_username", "your_password")

# Request only specific fields
quotes = client.get_quote(
    symbols=["PETR4", "VALE3"],
    fields=["ULT", "VAR", "VOLUME"]
)
```

#### Manual Token Management

```python
client = Broadcast("your_username", "your_password")

# Check current token
print(f"Token: {client.token}")
print(f"Refresh Token: {client.refresh_token}")

# Refresh token manually
result = client.token_refresh()
if result["success"]:
    print("Token refreshed successfully")
```

#### Error Handling

```python
import httpx
from broadcast import Broadcast

try:
    client = Broadcast("username", "password")
    quotes = client.get_quote(["PETR4"])
except httpx.RequestError as e:
    print(f"Connection error: {e}")
except httpx.HTTPStatusError as e:
    print(f"HTTP error {e.response.status_code}")
```

## 🔧 API Reference

### `Broadcast`

#### Initialization

```python
Broadcast(usr: str, pwd: str, keep_alive: bool = False, verify_ssl: bool = True)
```

**Parameters:**
- `usr` (str): Username for authentication
- `pwd` (str): Password for authentication
- `keep_alive` (bool, optional): If `True`, keeps the session alive. Default: `False`
- `verify_ssl` (bool, optional): If `True`, verifies SSL certificates. Default: `True`

**Raises:**
- `httpx.RequestError`: Connection or SSL error
- `httpx.HTTPStatusError`: HTTP error returned by the API

#### Methods

##### `login(usr: str, pwd: str) -> dict[str, str]`

Perform login against the API and return authentication tokens.

**Returns:** Dictionary containing `token` and `refreshToken`

##### `logout() -> dict[str, Any]`

Log out from the API, invalidating the current token.

**Returns:** Response from the API after logout

##### `keep_alive() -> dict[str, Any]`

Keep the current API session alive.

**Returns:** Response from the API for the keep-alive request

##### `token_refresh() -> dict[str, Any] | bool`

Refresh the authentication token using the refresh token.

**Returns:** Result of the refresh operation or `False` on error

##### `get_quote(symbols: list[str], fields: list[str] = None) -> dict[str, Any]`

Retrieve quotes for the requested financial instruments.

**Parameters:**
- `symbols` (list[str]): List of instrument symbols
- `fields` (list[str], optional): List of desired fields. Default: all fields

**Returns:** Quote payload or error message

## 🛠️ Development

### Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) - Modern Python package manager
- [httpx](https://www.python-httpx.org/) - HTTP client

### Environment Setup

```bash
# Install uv
pip install uv

# Sync dependencies
uv sync --locked --all-extras --dev
```

### Running Tests

```bash
# Run all tests with coverage
uv run pytest --cov --cov=broadcast --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_datafeed.py -v
```

### Linting

```bash
# Check code with ruff
uv run ruff check .

# Auto-fix issues when possible
uv run ruff check . --fix
```

### Project Structure

```
broadcast/
├── src/
│   └── broadcast/
│       ├── __init__.py      # Package exports
│       ├── datafeed.py      # Main Broadcast class
│       └── py.typed         # PEP 561 marker
├── tests/
│   └── test_datafeed.py     # Unit tests
├── .github/
│   └── workflows/           # CI/CD with GitHub Actions
├── pyproject.toml           # Project configuration
├── pytest.ini               # Pytest configuration
├── LICENSE                  # MIT License
└── README.md                # This file
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for more details on how to contribute.

### Contribution Process

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/MyFeature`)
3. Commit your changes (`git commit -m 'Add MyFeature'`)
4. Push to the branch (`git push origin feature/MyFeature`)
5. Open a Pull Request

## ⚠️ Security Notes

**Important:** The current version allows disabling SSL verification via `verify_ssl=False`, which should only be used in development environments. For production use, always keep SSL verification enabled (default behavior).

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Sylvio Campos Neto**  
- Email: [sylvio.campos@gmail.com.br](mailto:sylvio.campos@gmail.com.br)
- GitHub: [@sylvioCampos](https://github.com/sylvioCampos)

## 🙏 Acknowledgments

- AEBroadcast for the financial data API
- Python community and `httpx` maintainers

---

**Note:** This is an unofficial client for the AEBroadcast API.
