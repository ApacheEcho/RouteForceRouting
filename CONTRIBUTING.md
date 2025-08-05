# Contributing to RouteForceRouting

Thank you for your interest in contributing to RouteForceRouting! This guide will help you understand our development process and how to contribute effectively.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Google Maps API key (for full functionality)

### Development Environment Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/RouteForceRouting.git
   cd RouteForceRouting
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env  # If available, or create manually
   
   # Add your API keys to .env
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   GOOGLE_MAPS_API_SECRET=your_google_maps_api_secret_here
   ```

4. **Verify setup**
   ```bash
   # Run basic tests
   python -m pytest tests/ -v
   
   # Check code style
   flake8 .
   black --check .
   ```

## 📋 How to Contribute

### Reporting Issues

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the issue templates** when available
3. **Provide detailed information**:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs. actual behavior
   - Environment details (Python version, OS, etc.)
   - Error messages or logs
   - Screenshots for UI issues

#### Issue Types

- **🐛 Bug Report**: For reporting unexpected behavior
- **✨ Feature Request**: For suggesting new functionality
- **📚 Documentation**: For documentation improvements
- **🔧 Enhancement**: For improving existing features
- **❓ Question**: For general questions about usage

### Pull Request Process

#### 1. Before You Start

- **Discuss major changes** by creating an issue first
- **Check existing PRs** to avoid duplicate work
- **Read the project roadmap** in README.md

#### 2. Development Workflow

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description

# 2. Make your changes
# Follow the coding standards below

# 3. Test your changes
python -m pytest tests/ -v
python -m pytest -k "your_test" -v  # Run specific tests

# 4. Format your code
black .
isort .
flake8 .

# 5. Commit your changes
git add .
git commit -m "feat: add route optimization caching"
# Use conventional commit messages (see below)

# 6. Push and create PR
git push origin feature/your-feature-name
```

#### 3. Pull Request Guidelines

- **Fill out the PR template** completely
- **Link related issues** using "Fixes #123" or "Closes #123"
- **Keep PRs focused** - one feature/fix per PR
- **Write clear commit messages** using conventional commits
- **Add tests** for new functionality
- **Update documentation** if needed
- **Ensure CI passes** before requesting review

#### 4. Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(routing): add genetic algorithm optimization
fix(api): resolve geocoding cache corruption
docs: update installation instructions
test(core): add integration tests for route scoring
```

## 🎯 Code Standards

### Python Code Style

We enforce code quality using automated tools:

#### Formatting
- **Black**: Code formatting
  ```bash
  black .  # Format all Python files
  black --check .  # Check without formatting
  ```

- **isort**: Import sorting
  ```bash
  isort .  # Sort imports
  isort --check-only .  # Check without sorting
  ```

#### Linting
- **flake8**: Code style and quality
  ```bash
  flake8 .  # Check all files
  flake8 app/  # Check specific directory
  ```

#### Configuration Files
- `.flake8` or `setup.cfg`: flake8 configuration
- `pyproject.toml`: Black and isort configuration
- `.editorconfig`: Editor configuration

### Code Quality Guidelines

1. **Follow PEP 8** Python style guide
2. **Write clear, descriptive variable names**
   ```python
   # Good
   optimized_route_distance = calculate_total_distance(route)
   
   # Avoid
   d = calc_dist(r)
   ```

3. **Add docstrings** for modules, classes, and functions
   ```python
   def optimize_route(stores, algorithm='genetic'):
       """Optimize route for visiting multiple stores.
       
       Args:
           stores (List[Store]): List of store locations
           algorithm (str): Optimization algorithm to use
           
       Returns:
           OptimizedRoute: The optimized route with metrics
           
       Raises:
           ValueError: If algorithm is not supported
       """
   ```

4. **Handle errors gracefully**
   ```python
   try:
       result = geocode_address(address)
   except GeocodeError as e:
       logger.error(f"Geocoding failed for {address}: {e}")
       raise
   ```

5. **Use type hints** where appropriate
   ```python
   from typing import List, Optional
   
   def calculate_distance(start: Location, end: Location) -> float:
       return distance_between_points(start.lat, start.lng, end.lat, end.lng)
   ```

## 🧪 Testing Standards

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for workflows
├── fixtures/       # Test data and fixtures
└── conftest.py     # Pytest configuration
```

### Writing Tests

1. **Use descriptive test names**
   ```python
   def test_route_optimization_returns_shortest_path():
   def test_geocoding_cache_prevents_duplicate_api_calls():
   def test_invalid_address_raises_geocode_error():
   ```

2. **Follow AAA pattern** (Arrange, Act, Assert)
   ```python
   def test_route_distance_calculation():
       # Arrange
       start = Location(lat=40.7128, lng=-74.0060)
       end = Location(lat=40.7589, lng=-73.9851)
       
       # Act
       distance = calculate_distance(start, end)
       
       # Assert
       assert distance > 0
       assert isinstance(distance, float)
   ```

3. **Use fixtures** for reusable test data
   ```python
   @pytest.fixture
   def sample_stores():
       return [
           Store(name="Store A", address="123 Main St"),
           Store(name="Store B", address="456 Oak Ave"),
       ]
   ```

4. **Mock external dependencies**
   ```python
   @patch('routing.utils.requests.get')
   def test_geocoding_api_call(mock_get):
       mock_get.return_value.json.return_value = {'lat': 40.7128, 'lng': -74.0060}
       result = geocode_address("123 Main St")
       assert result.lat == 40.7128
   ```

### Test Coverage

- **Aim for >80% test coverage** for new code
- **Test critical paths** thoroughly (route optimization, data loading)
- **Include edge cases** and error conditions
- **Add integration tests** for complete workflows

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run specific test files
python -m pytest tests/test_routing.py -v

# Run tests matching pattern
python -m pytest -k "test_optimization" -v

# Run tests for specific module
python -m pytest tests/unit/test_core.py::test_route_optimization -v
```

## 📁 Project Structure

Understanding the codebase organization:

```
RouteForceRouting/
├── app/                    # Flask application
│   ├── __init__.py        # App factory
│   ├── api/               # API routes
│   ├── auth/              # Authentication
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   ├── static/            # Static files (CSS, JS)
│   └── templates/         # HTML templates
├── routing/                # Core routing engine
│   ├── core.py            # Route optimization algorithms
│   ├── loader.py          # Data loading and validation
│   ├── utils.py           # Utilities (geocoding, distance)
│   └── config.py          # Configuration
├── tests/                  # Test suite
├── migrations/             # Database migrations
├── scripts/                # Utility scripts
├── docs/                   # Documentation
├── .github/                # GitHub templates and workflows
├── requirements.txt        # Python dependencies
├── pytest.ini            # Pytest configuration
├── .env.example           # Environment variable template
└── README.md              # Project overview
```

### Key Modules

- **`routing/core.py`**: Route optimization algorithms
- **`routing/loader.py`**: Data loading and validation
- **`routing/utils.py`**: Geocoding, caching, distance calculations
- **`app/api/`**: REST API endpoints
- **`app/services/`**: Business logic services
- **`tests/`**: Comprehensive test suite

## 🔄 Development Workflow

### Branching Strategy

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: Feature development branches
- **`fix/*`**: Bug fix branches
- **`hotfix/*`**: Critical production fixes

### Code Review Process

1. **Automated checks** must pass (CI/CD)
2. **At least one review** from maintainers
3. **All conversations resolved** before merge
4. **Up-to-date with target branch**

### Release Process

1. Features merged to `develop`
2. Release candidate created from `develop`
3. Final testing and bug fixes
4. Merge to `main` and tag release
5. Deploy to production

## 💬 Communication Guidelines

### Code Review Etiquette

- **Be constructive** and specific in feedback
- **Explain the "why"** behind suggestions
- **Ask questions** instead of making demands
- **Acknowledge good work** and improvements
- **Focus on the code**, not the person

### Getting Help

- **Check documentation** first (README, docs/)
- **Search existing issues** and discussions
- **Ask questions** in issue comments
- **Be patient** with response times
- **Provide context** when asking for help

## 🏆 Recognition

We appreciate all contributions! Contributors will be:

- **Listed in CONTRIBUTORS.md** (if it exists)
- **Mentioned in release notes** for significant contributions
- **Credited in documentation** for major features

## 📞 Contact

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Security**: Email security issues privately to maintainers

## 📜 License

By contributing to RouteForceRouting, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to RouteForceRouting! Your efforts help make route optimization better for everyone. 🚀