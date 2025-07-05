# Contributing to IntentGraph

## Development Setup
- Python 3.12+ installation
- Virtual environment setup
- Dependencies installation: `pip install -r requirements-dev.txt`

## Code Style
- Follow PEP 8 guidelines
- Use ruff for formatting: `ruff format .`
- Use mypy for type checking: `mypy .`
- Security scanning: `bandit -r src/`

## Testing
- Write tests for new features
- Run test suite: `pytest --cov=intentgraph`
- Maintain 90% code coverage

## Pull Request Process
- Fork repository
- Create feature branch
- Write tests
- Update documentation
- Submit PR with clear description

## Issue Reporting
- Use GitHub Issues
- Include reproduction steps
- Provide sample code/repository