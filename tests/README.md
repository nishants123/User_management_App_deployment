# Running Tests

This project uses pytest for unit and integration testing with comprehensive coverage.

## Installation

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

## Running Tests Locally

### Run all tests:

```bash
pytest
```

### Run with coverage report:

```bash
pytest --cov=. --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

### Run specific test file:

```bash
pytest tests/test_app.py
```

### Run specific test class:

```bash
pytest tests/test_app.py::TestGetUsersEndpoint
```

### Run specific test function:

```bash
pytest tests/test_app.py::TestGetUsersEndpoint::test_get_users_success
```

### Run only unit tests:

```bash
pytest -m "not integration"
```

### Run only integration tests:

```bash
pytest -m integration
```

### Verbose output:

```bash
pytest -v
```

## Test Structure

- **tests/conftest.py** - Pytest configuration and shared fixtures
- **tests/test_app.py** - Unit tests for Flask endpoints and utility functions
- **tests/test_integration.py** - Integration tests for complete workflows

## Test Coverage

The project aims for high test coverage. Coverage report is automatically generated when running pytest.

## CI/CD Pipeline

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

The CI pipeline is defined in `.github/workflows/tests.yml` and:
1. Tests on Python 3.8, 3.9, and 3.10
2. Generates coverage reports
3. Uploads to Codecov (optional)

## Mock Database

Tests use mocked database connections to avoid requiring a running MySQL server. This makes tests:
- Fast and isolated
- Reliable
- Independent of external services

## What's Tested

### Endpoints
- ✅ GET /health - Health check
- ✅ GET /users - Fetch all users
- ✅ GET /users/<id> - Fetch specific user
- ✅ POST /users - Create new user
- ✅ PUT /users/<id> - Update user
- ✅ DELETE /users/<id> - Delete user
- ✅ POST /backup - Trigger backup
- ✅ GET / - Index page

### Validation
- ✅ Email format validation
- ✅ Required fields validation
- ✅ Duplicate email detection

### Error Handling
- ✅ Database connection failures
- ✅ User not found scenarios
- ✅ Invalid input handling
