# Running Tests

This project uses pytest for comprehensive testing with extensive coverage across unit, integration, functional, security, and API tests.

## Total Test Count

**120+ tests** covering all aspects of the application

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

### Core Tests
- **conftest.py** - Pytest configuration and shared fixtures
- **test_app.py** - Unit tests for Flask endpoints and utility functions (40+ tests)
- **test_integration.py** - Integration tests for complete user CRUD workflows

### Advanced Tests
- **test_api_advanced.py** - Advanced API testing:
  - Edge cases and boundary conditions
  - Input validation (unicode, special characters, length limits)
  - Error handling and recovery
  - Response format consistency
  - XSS/injection protection validation

- **test_database.py** - Database operation tests:
  - Connection lifecycle management
  - Transaction commit/rollback behavior
  - SQL injection protection verification
  - Concurrent operations
  - Data integrity and uniqueness constraints
  - Connection pool handling

- **test_security.py** - Security and functional behavior:
  - SQL injection protection
  - Input sanitization
  - Backup functionality verification
  - HTTP method handling
  - Response headers validation

- **test_functional.py** - End-to-end and functional tests:
  - HTML template rendering
  - Complete user management workflows
  - Error recovery scenarios
  - Data consistency validation
  - Request/response format consistency

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

### Endpoints (test_app.py)
- ✅ GET /health - Health check
- ✅ GET /users - Fetch all users
- ✅ GET /users/<id> - Fetch specific user
- ✅ POST /users - Create new user
- ✅ PUT /users/<id> - Update user
- ✅ DELETE /users/<id> - Delete user
- ✅ POST /backup - Trigger backup
- ✅ GET / - Index page (template rendering)

### Validation (test_app.py, test_api_advanced.py)
- ✅ Email format validation
- ✅ Required fields validation
- ✅ Special characters and unicode support
- ✅ Very long inputs
- ✅ Whitespace handling
- ✅ Null value handling

### Error Handling (test_app.py, test_api_advanced.py, test_database.py)
- ✅ Database connection failures
- ✅ User not found scenarios
- ✅ Invalid input handling
- ✅ Duplicate email detection
- ✅ Database transaction errors
- ✅ Cursor and connection lifecycle errors
- ✅ Recovery after errors

### Database (test_database.py)
- ✅ Connection lifecycle management
- ✅ Transaction commit/rollback
- ✅ Parameterized queries (SQL injection protection)
- ✅ Bulk operations (100+ users)
- ✅ None/null value handling
- ✅ Concurrent read operations
- ✅ Data integrity verification
- ✅ Email uniqueness constraints

### Security (test_security.py)
- ✅ SQL injection protection
- ✅ XSS protection validation
- ✅ Path traversal protection
- ✅ Email header injection protection
- ✅ Input sanitization with special characters
- ✅ HTML tag handling in inputs

### Functional (test_functional.py)
- ✅ HTML template rendering
- ✅ Complete user CRUD workflows
- ✅ Multiple user scenarios
- ✅ Backup triggered on create/update/delete
- ✅ Response format consistency
- ✅ Error recovery workflows
- ✅ HTTP method handling
- ✅ Content type validation

### API (test_api_advanced.py)
- ✅ Edge cases and boundary conditions
- ✅ Empty responses
- ✅ Special character handling
- ✅ Response format validation
- ✅ Error response structures
- ✅ Health endpoint format
