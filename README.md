# PyShort - Python URL Shortener v2

A modern, efficient URL shortener service built with Python.

## Features

- Fast URL shortening and redirection
- Configurable storage backends
- RESTful API
- Comprehensive test coverage

## Installation

```bash
pip install pyshort
```

Or for development:

```bash
git clone <repository-url>
cd pyshort
pip install -e ".[dev]"
```

## Quick Start

```python
from pyshort import Shortener

shortener = Shortener()
short_url = shortener.shorten("https://example.com/very/long/url")
print(short_url)  # Outputs: https://short.domain/abc123
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

### Type Checking

```bash
mypy pyshort
```

## Project Structure

```
pyshort/
├── pyshort/           # Main package
│   └── __init__.py
├── tests/             # Test suite
│   └── __init__.py
├── pyproject.toml     # Project configuration
├── README.md          # This file
└── LICENSE            # MIT License
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.