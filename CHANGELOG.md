# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-12

### Added
- Support for loading a custom CA bundle via `ssl_pem_path`
- `certifi` as a runtime dependency for a reliable default CA store

### Changed
- When `verify_ssl=True`, the client now configures `httpx` verification using an `ssl.SSLContext`

## [1.0.0] - 2025-01-31

### Added
- Complete test suite with 98% code coverage
- Support for SSL certificate verification (enabled by default)
- Comprehensive error handling with specific httpx exceptions
- MIT License for public distribution
- Full English documentation (README, CONTRIBUTING, docstrings)
- Type hints throughout the codebase (PEP 484 compliant)
- Keep-alive mechanism for maintaining active sessions

### Changed
- Improved API client initialization with better parameter handling
- Enhanced documentation with detailed examples and API reference
- Updated error messages to be more descriptive and actionable
- Refactored authentication flow for better maintainability
- Converted all Portuguese documentation to English for PEP compliance

### Security
- SSL verification now enabled by default (can be disabled if needed)
- Secure token handling and storage

## [0.1.0] - Initial Release

### Added
- Initial implementation of Broadcast API client
- Basic authentication (login/logout)
- Token management (refresh tokens)
- Stock quote retrieval functionality
- Environment variable support for credentials
