# Contributing Guide

Thank you for considering contributing to the Broadcast project! This document provides guidelines to help you contribute effectively.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Environment Setup](#development-environment-setup)
- [Development Process](#development-process)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a code of conduct based on the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code.

### Our Standards

- Be respectful and inclusive with other contributors
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please:

1. Check if the bug has not already been reported in [Issues](https://github.com/sylvioCampos/broadcast/issues)
2. If it doesn't exist, create a new issue including:
   - Descriptive title
   - Detailed steps to reproduce the problem
   - Expected behavior vs. actual behavior
   - Python version and operating system
   - Full stack trace (if applicable)

### Suggesting Enhancements

To suggest improvements:

1. Check if the suggestion doesn't already exist in Issues
2. Create a new issue with the `enhancement` tag including:
   - Clear description of the enhancement
   - Motivation and use cases
   - Examples of how the functionality would be used

### Contributing Code

1. Fork the repository
2. Create a branch for your feature/fix
3. Implement your changes
4. Add/update tests
5. Verify all tests pass
6. Submit a Pull Request

## Development Environment Setup

### Prerequisites

- Python 3.14 or higher
- Git
- [uv](https://github.com/astral-sh/uv) - Python package manager

### Setup Steps

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/broadcast.git
cd broadcast

# 2. Install uv (if you don't have it)
pip install uv

# 3. Sync dependencies
uv sync --locked --all-extras --dev

# 4. Verify installation
uv run pytest --version
```

## Development Process

### 1. Create a Branch

```bash
git checkout -b feature/feature-name
# or
git checkout -b fix/bugfix-name
```

Naming convention:
- `feature/` - For new features
- `fix/` - For bug fixes
- `docs/` - For documentation changes
- `refactor/` - For code refactorings
- `test/` - For adding/improving tests

### 2. Make Your Changes

- Write clean and readable code
- Follow the project's code standards (see below)
- Add docstrings for new functions/classes
- Comment complex code when necessary

### 3. Add Tests

- All new code must have corresponding tests
- Maintain test coverage above 95%
- Run tests locally:

```bash
uv run pytest --cov --cov=broadcast --cov-report=term-missing
```

### 4. Check Code

```bash
# Run linter
uv run ruff check .

# Auto-fix issues when possible
uv run ruff check . --fix
```

## Code Standards

### Code Style

This project follows:
- **PEP 8** - Python style guide
- **PEP 484** - Type Hints
- **PEP 257** - Docstring Conventions

### Type Hints

Always use type hints:

```python
def example_function(parameter: str, optional: int = 0) -> dict[str, Any]:
    """Example function with type hints."""
    return {"result": parameter}
```

### Docstrings

Use Google Style format:

```python
def example_method(arg1: str, arg2: int) -> bool:
    """
    Brief description of what the method does.

    More detailed description if needed, explaining behavior,
    special cases, etc.

    Args:
        arg1 (str): Description of the first argument.
        arg2 (int): Description of the second argument.

    Returns:
        bool: Description of the return value.

    Raises:
        ValueError: When arg2 is negative.
        TypeError: When arg1 is not a string.

    Examples:
        >>> result = example_method("test", 5)
        >>> print(result)
        True
    """
    pass
```

### Error Handling

- Use specific `httpx` exceptions when appropriate
- Always document exceptions that can be raised
- Catch specific exceptions, don't use generic `except Exception:`

```python
try:
    response = self.client.get(url)
    response.raise_for_status()
except httpx.RequestError as e:
    print(f"Request error: {e}")
    raise
except httpx.HTTPStatusError as e:
    print(f"HTTP error: {e.response.status_code}")
    raise
```

## Testing

### Test Structure

- Use `pytest` as the testing framework
- Organize tests in classes when appropriate
- Use fixtures for common setup
- Mock external calls (HTTP, etc.)

### Test Example

```python
def test_method_success(self, mock_client):
    """Tests if the method works correctly on success."""
    # Setup
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test"}
    mock_client.get.return_value = mock_response

    # Execute
    client = Broadcast("user", "pass")
    result = client.method()

    # Assert
    assert result == {"data": "test"}
    mock_client.get.assert_called_once()
```

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov --cov=broadcast --cov-report=term-missing

# Specific test
uv run pytest tests/test_datafeed.py::TestBroadcast::test_login_success -v

# With detailed output
uv run pytest -vv
```

## Pull Request Process

### Before Submitting

- [ ] All tests pass locally
- [ ] Test coverage maintained or improved (>95%)
- [ ] Code passes linter (ruff)
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (if applicable)
- [ ] Commits with descriptive messages

### Commit Messages

Use clear and descriptive messages:

```
Add method to fetch price history

- Implement new /history endpoint
- Add unit tests
- Update API documentation
```

Conventions:
- Use present tense ("Add" not "Added")
- First line: concise summary (50 characters or less)
- Body: additional details if needed
- Reference issues: "Closes #123"

### Submitting the Pull Request

1. Push your branch to GitHub:
```bash
git push origin feature/feature-name
```

2. Go to the repository on GitHub and click "New Pull Request"

3. Fill in the PR template including:
   - Clear description of changes
   - Motivation and context
   - Type of change (bugfix, feature, docs, etc.)
   - Verification checklist
   - Screenshots (if applicable)

4. Wait for review:
   - Respond to feedback constructively
   - Make requested changes
   - Keep the branch up to date with `main`

### Code Review

After submitting the PR:

- Maintainers will review your code
- There may be requests for changes
- Discussions are welcome
- Be patient and respectful

## Questions?

If you have questions about the contribution process:

1. Check the [documentation](README.md)
2. Search [Closed Issues](https://github.com/sylvioCampos/broadcast/issues?q=is%3Aissue+is%3Aclosed)
3. Open a new issue with the `question` tag

## License

By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) as the project.

---

Thank you for contributing! 🎉
