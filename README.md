# FlowHub Web Automation Framework

Production-grade web automation framework for FlowHub application testing.

## Features

- ✅ **Parallel Execution** - 8 workers for 8x faster tests
- ✅ **Smart Auth** - Token validation with automatic refresh
- ✅ **Lazy Loading** - Only creates data needed by selected tests
- ✅ **Test Context Pattern** - Industry-standard state management
- ✅ **Seed Data Strategy** - Persistent baseline + transient test data
- ✅ **Page Object Model** - Maintainable UI abstraction
- ✅ **Retry Logic** - 3-layer flakiness handling
- ✅ **Allure Reports** - Rich HTML reports with screenshots

## Tech Stack

- **Python 3.11+**
- **Playwright** - Browser automation
- **Pytest** - Test framework
- **pytest-xdist** - Parallel execution
- **Allure** - Reporting

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Run Tests

```bash
# Local environment (default)
pytest

# Staging environment
pytest --env=staging

# Production environment
pytest --env=production

# Smoke tests on staging
pytest --env=staging -m smoke

# Show browser (headed mode)
$env:HEADLESS="false"; pytest

# Specific browser
$env:BROWSER="firefox"; pytest
```

## Project Structure

```
├── config/           # Configuration
│   ├── settings.py
│   └── browser_config.py
├── data/             # Test data
│   ├── users.json
│   └── test_data.py
├── pages/            # Page objects
│   ├── base_page.py
│   ├── login_page.py
│   ├── items_page.py
│   └── ...
├── tests/            # Test files
│   ├── conftest.py
│   ├── test_auth.py
│   └── ...
├── utils/            # Utilities
│   ├── api_client.py
│   ├── logger.py
│   └── exceptions.py
└── docs/             # Documentation
    └── ARCHITECTURE.md
```

## Test Execution

### Smoke Tests (~1 minute)
```bash
pytest -m smoke
```

### Full Regression (~5 minutes)
```bash
pytest -n 8
```

### Single Test
```bash
pytest tests/test_auth.py::TestAuthentication::test_successful_login
```

## Environment Variables

```bash
# Application URL
BASE_URL=https://testing-box.vercel.app

# Browser settings
HEADLESS=true
BROWSER=chromium

# Parallel workers
PYTEST_WORKERS=8
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - Complete framework design
- [Framework Overview](docs/FRAMEWORK_OVERVIEW.md) - Quick reference
- [Test Cases](docs/WEB_TEST_CASES.md) - All test scenarios
- [Test Data Strategy](docs/TEST_DATA_STRATEGY.md) - Data management

## CI/CD

GitHub Actions workflow runs on every commit:
- Parallel matrix builds (Chromium, Firefox, WebKit)
- Allure report generation
- Screenshot capture on failures

## Author

Senior SDET - 10+ years experience
