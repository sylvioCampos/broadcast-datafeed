[![Build Status](https://github.com/sylvioCampos/broadcast/actions/workflows/python-uv-build.yml/badge.svg)](https://github.com/sylvioCampos/broadcast/actions)
[![Coverage Status](https://codecov.io/gh/sylvioCampos/broadcast/branch/main/graph/badge.svg)](https://codecov.io/gh/sylvioCampos/broadcast)
[![Last Commit](https://img.shields.io/github/last-commit/sylvioCampos/broadcast.svg)](https://github.com/sylvioCampos/broadcast/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Broadcast

A Python client for interacting with the AEBroadcast API service.  
This package provides authentication and methods to retrieve financial data, such as stock quotes, from the AEBroadcast platform.

## Features

- Simple authentication with the AEBroadcast API
- Retrieve stock quotes and financial data
- Secure HTTPS connections using truststore and SSL

## Installation

```bash
pip install git+https://github.com/yourusername/broadcast.git
```

Or add to your `requirements.txt`:

```
git+https://github.com/yourusername/broadcast.git
```

## Usage

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

## API

### `Broadcast`

#### Initialization

```python
Broadcast(usr: str, pwd: str, keep_alive: bool = False)
```

- `usr`: Username for authentication.
- `pwd`: Password for authentication.
- `keep_alive`: (optional) If `True`, keeps the session alive.

#### Methods

- `get_quote(symbols: list[str], fields: list[str] = None) -> dict`
- `logout() -> dict`
- `keep_alive() -> dict`
- `token_refresh() -> dict | bool`

## Requirements

- Python 3.10+
- [httpx](https://www.python-httpx.org/)
- [truststore](https://github.com/sethmlarson/truststore)

## License

MIT License © 2025 Warren Investimentos

## Author

Sylvio Campos Neto  
[sylvio.campos@warren.com.br](mailto:sylvio.campos@warren.com.br)
