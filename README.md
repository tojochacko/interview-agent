# Conversation Agent v11

Testing conversational agents with multiple TTS (Text-to-Speech) system providers.

## Setup

### Prerequisites
- Python 3.9 or higher

### Installation

1. Create and activate the virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# Or on Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

## Development

### Code Quality
This project uses Ruff for linting and formatting:
```bash
# Check code
ruff check .

# Format code
ruff format .
```

### Testing
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov
```

## Project Structure

```
conversation-agent-v11/
├── src/
│   └── conversation_agent/    # Main application code
├── tests/                     # Test files
├── features/                  # Feature planning documents
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Development Guidelines

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines and principles.
