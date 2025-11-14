# Dynite

[![PyPI version](https://img.shields.io/pypi/v/dynite)](https://pypi.org/project/dynite/)
[![Python versions](https://img.shields.io/badge/python-3.13-blue)](https://pypi.org/project/dynite/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust and efficient Python client for Microsoft Business Central OData API.

## Overview

Dynite simplifies interactions with the Microsoft Business Central OData API by providing a high-level, Pythonic interface for fetching business data. It automatically handles authentication, pagination, retry logic, and error handling, allowing developers to focus on their business logic rather than API mechanics.

### Key Features

- 🚀 **Simple API**: Easy-to-use client for Business Central OData endpoints
- 📄 **Automatic Pagination**: Handles large datasets with transparent pagination
- 🔄 **Retry Logic**: Configurable retry mechanism for transient failures
- 🛡️ **Error Handling**: Comprehensive exception hierarchy for different error types
- 📝 **Type Hints**: Full type annotations for better IDE support and code completion
- 📊 **Logging**: Built-in logging support for debugging and monitoring
- 🐍 **Modern Python**: Requires Python 3.13+ for optimal performance and features

## Installation

### From PyPI (Recommended)

```bash
pip install dynite
```

### From Source

```bash
# Clone the repository
git clone https://github.com/prabhuakshay/dynite.git
cd dynite

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

### Development Installation

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

## Quick Start

```python
from dynite import Dynite

# Initialize the client
client = Dynite(
    base_url="https://api.businesscentral.dynamics.com/v2.0/tenant_id/api/v2.0",
    auth=("username", "password")
)

# Fetch all companies
companies = client.get_records("companies")
print(f"Found {len(companies)} companies")

# Fetch customers with filtering
customers = client.get_records("customers", params={"$filter": "status eq 'active'"})
```

## API Reference

### Dynite Class

The main client class for interacting with Business Central OData API.

#### Constructor

```python
Dynite(
    base_url: str,
    auth: tuple[str, str],
    timeout: int = 30,
    retries: int = 3
)
```

**Parameters:**
- `base_url` (str): The base URL for the Business Central OData API endpoint. Must be a valid HTTPS URL.
- `auth` (tuple[str, str]): Authentication credentials as (username, password) tuple for basic authentication.
- `timeout` (int, optional): Request timeout in seconds. Defaults to 30 seconds.
- `retries` (int, optional): Number of retry attempts for failed requests. Defaults to 3.

**Raises:**
- `InvalidURLError`: If the provided base_url is not a valid URL.

**Example:**
```python
client = Dynite(
    base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/api/v2.0",
    auth=("your-username", "your-password"),
    timeout=60,
    retries=5
)
```

#### Methods

##### `get_records(endpoint: str, params: dict[str, str] | None = None) -> list[dict[str, Any]]`

Retrieves all records from the specified API endpoint with automatic pagination.

This method handles OData pagination transparently, following `@odata.nextLink` until all records are retrieved. It first fetches the record count to provide progress information.

**Parameters:**
- `endpoint` (str): The API endpoint path (e.g., "companies", "customers", "salesOrders"). Leading slashes are automatically handled.
- `params` (dict[str, str], optional): OData query parameters for filtering, sorting, expanding, etc.

**Returns:**
- `list[dict[str, Any]]`: List of records as dictionaries, where each dictionary represents one entity with all its fields.

**Raises:**
- `InvalidResponseError`: If the API returns invalid JSON or unexpected response format.
- `FailedRequestError`: If the HTTP request fails after all retry attempts.

**Examples:**

```python
# Basic usage
companies = client.get_records("companies")

# With filtering
active_customers = client.get_records("customers", {
    "$filter": "status eq 'active'",
    "$orderby": "name",
    "$top": "100"
})

# With expansion (related entities)
sales_orders = client.get_records("salesOrders", {
    "$expand": "customer,salesOrderLines",
    "$filter": "status eq 'open'"
})
```

## Advanced Usage

### Query Parameters

Dynite supports all standard OData query parameters:

```python
# Filtering
params = {"$filter": "amount gt 1000 and date gt 2024-01-01"}

# Sorting
params = {"$orderby": "createdDate desc, amount asc"}

# Selecting specific fields
params = {"$select": "id,name,email,status"}

# Expanding related entities
params = {"$expand": "customer,salesOrderLines"}

# Pagination (handled automatically, but can be limited)
params = {"$top": "500"}

# Combining parameters
params = {
    "$filter": "status eq 'active'",
    "$orderby": "name",
    "$select": "id,name,email",
    "$expand": "contact",
    "$top": "1000"
}

records = client.get_records("customers", params=params)
```

### Error Handling

Dynite provides a comprehensive exception hierarchy for different error scenarios:

```python
from dynite.exceptions import (
    DyniteError,           # Base exception for all Dynite errors
    InvalidURLError,       # Invalid base URL provided
    InvalidResponseError,  # Malformed API response
    FailedRequestError     # HTTP request failure
)

try:
    records = client.get_records("companies")
    print(f"Retrieved {len(records)} companies")

except InvalidURLError as e:
    print(f"Invalid API URL: {e}")
    # Check your base_url configuration

except FailedRequestError as e:
    print(f"Request failed: {e}")
    # Check network connectivity, credentials, or API availability

except InvalidResponseError as e:
    print(f"Invalid API response: {e}")
    # API returned unexpected data format

except DyniteError as e:
    print(f"Dynite error: {e}")
    # Catch-all for any Dynite-related error
```

### Logging

Dynite uses Python's standard logging module. Configure logging to monitor API interactions:

```python
import logging

# Basic logging
logging.basicConfig(level=logging.INFO)

# Detailed logging with timestamps
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# File logging
logging.basicConfig(
    filename='dynite.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create logger and set level
logger = logging.getLogger('dynite')
logger.setLevel(logging.DEBUG)
```

### Environment Variables

Configure the client using environment variables for better security:

```bash
export BUSINESS_CENTRAL_URL="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/api/v2.0"
export BUSINESS_CENTRAL_USER="your_username"
export BUSINESS_CENTRAL_PASSWORD="your_password"
```

```python
import os
from dynite import Dynite

client = Dynite(
    base_url=os.getenv("BUSINESS_CENTRAL_URL"),
    auth=(os.getenv("BUSINESS_CENTRAL_USER"), os.getenv("BUSINESS_CENTRAL_PASSWORD"))
)
```

### Custom Session Configuration

For advanced use cases, you can modify the client's session:

```python
from dynite import Dynite
import requests

client = Dynite(base_url="...", auth=("user", "pass"))

# Add custom headers
client.session.headers.update({
    "User-Agent": "MyApp/1.0",
    "X-Custom-Header": "value"
})

# Configure proxies
client.session.proxies = {
    "https": "https://proxy.company.com:8080"
}

# Add custom authentication
from requests.auth import HTTPBasicAuth
client.session.auth = HTTPBasicAuth("user", "pass")
```

## Configuration Options

### Timeout Settings

```python
# Short timeout for fast networks
client = Dynite(base_url="...", auth=("user", "pass"), timeout=10)

# Long timeout for slow networks
client = Dynite(base_url="...", auth=("user", "pass"), timeout=120)
```

### Retry Configuration

```python
# Aggressive retries for unreliable networks
client = Dynite(base_url="...", auth=("user", "pass"), retries=10)

# No retries for debugging
client = Dynite(base_url="...", auth=("user", "pass"), retries=0)
```

## Business Central API Integration

### Authentication

Dynite uses Basic Authentication with Business Central. Ensure your user account has appropriate permissions:

1. **Web Service Access Key**: Generate a web service access key in Business Central
2. **User Permissions**: Assign appropriate permissions to the user account
3. **Company Access**: Ensure the user has access to the required companies

### Common Endpoints

```python
# Company management
companies = client.get_records("companies")

# Customer management
customers = client.get_records("customers")
customer_details = client.get_records("customers", params={"$expand": "customerFinancialDetails"})

# Vendor management
vendors = client.get_records("vendors")

# Item management
items = client.get_records("items")
item_variants = client.get_records("itemVariants")

# Sales orders
sales_orders = client.get_records("salesOrders", params={"$expand": "salesOrderLines"})

# Purchase orders
purchase_orders = client.get_records("purchaseOrders")

# General ledger entries
gl_entries = client.get_records("generalLedgerEntries")

# Dimensions
dimensions = client.get_records("dimensions")
```

### Working with Large Datasets

Dynite automatically handles pagination, but you can optimize performance:

```python
# Process records in batches to manage memory
all_customers = []
page_size = 1000

# Note: $top limits the total results, not page size
customers = client.get_records("customers", params={"$top": str(page_size)})

# Process in chunks
for i in range(0, len(customers), 100):
    batch = customers[i:i+100]
    # Process batch
    process_customer_batch(batch)
```

## Troubleshooting

### Common Issues

#### Authentication Errors

**Problem:** `FailedRequestError: 401 Unauthorized`

**Solutions:**
- Verify username and password
- Check if web service access key is valid
- Ensure user has API permissions
- Confirm the account isn't locked

#### Invalid URL Errors

**Problem:** `InvalidURLError: Invalid URL`

**Solutions:**
- Verify the base URL format
- Ensure HTTPS is used
- Check tenant ID is correct
- Confirm the URL ends with the API version

#### Timeout Errors

**Problem:** `FailedRequestError: Request timed out`

**Solutions:**
- Increase timeout value: `Dynite(..., timeout=60)`
- Check network connectivity
- Verify Business Central service availability
- Consider API rate limiting

#### Large Dataset Issues

**Problem:** Memory errors with large result sets

**Solutions:**
- Use `$top` parameter to limit results
- Process records in batches
- Use `$select` to retrieve only needed fields
- Implement pagination manually if needed

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('dynite')
logger.setLevel(logging.DEBUG)

# This will show:
# - URL construction
# - Request/response details
# - Pagination progress
# - Error details
```

### Network Debugging

For network-level issues:

```python
import requests
import logging

# Enable requests logging
logging.getLogger("requests.packages.urllib3").setLevel(logging.DEBUG)
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.DEBUG)
```

## Development

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/prabhuakshay/dynite.git
cd dynite

# Install with development dependencies
uv pip install -e ".[dev]"

# Run all checks
task
```

### Available Tasks

| Task | Description |
|------|-------------|
| `task format` | Format code with Ruff |
| `task lint` | Run linting checks |
| `task fix` | Auto-fix linting issues |
| `task type-check` | Run type checking |
| `task test` | Run test suite |
| `task test-cov` | Run tests with coverage |
| `task clean` | Clean cache files |
| `task pre-commit` | Run pre-commit hooks |
| `task` | Run all checks (default) |

### Code Quality Tools

This project uses industry-standard tools for code quality:

- **Ruff**: Fast Python linter and formatter (replaces flake8, isort, black)
- **BasedPyright**: Strict type checking (Pyright fork)
- **Pytest**: Comprehensive test framework with coverage reporting
- **Pre-commit**: Git hooks for automated quality checks

### Testing

```bash
# Run all tests
task test

# Run with coverage
task test-cov

# Run specific test file
pytest tests/test_exceptions.py

# Run specific test
pytest tests/test_exceptions.py::TestDyniteExceptions::test_dynite_error_inherits_exception
```

### Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** following the code style
4. **Add tests** for new functionality
5. **Run all checks**: `task`
6. **Commit your changes**: `git commit -m "Add your feature"`
7. **Push to your fork**: `git push origin feature/your-feature-name`
8. **Create a Pull Request** on GitHub

### Code Style

This project follows strict code quality standards:

- **Google-style docstrings** for all public functions/classes
- **Type hints** for all function parameters and return values
- **88 character line length** (Black/Ruff standard)
- **Descriptive variable names** and comprehensive comments
- **Comprehensive test coverage** (aim for 90%+)

### Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v1.2.3`
4. Push tag: `git push origin v1.2.3`
5. GitHub Actions will automatically publish to PyPI

## Examples

### Complete Customer Management Script

```python
#!/usr/bin/env python3
"""
Complete example of customer data management with Dynite.
"""

import os
from dynite import Dynite
from dynite.exceptions import DyniteError

def main():
    # Initialize client
    client = Dynite(
        base_url=os.getenv("BC_URL"),
        auth=(os.getenv("BC_USER"), os.getenv("BC_PASSWORD")),
        timeout=60
    )

    try:
        # Get all active customers
        customers = client.get_records("customers", {
            "$filter": "status eq 'active'",
            "$orderby": "name",
            "$select": "id,name,email,phoneNumber",
            "$expand": "contact"
        })

        print(f"Found {len(customers)} active customers")

        # Process customers
        for customer in customers:
            print(f"- {customer['name']} ({customer['email']})")

        # Get customer count
        count_params = {"$filter": "status eq 'active'"}
        # Note: This would require a separate method for count-only queries
        # count = client.get_record_count("customers", count_params)

    except DyniteError as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
```

### Sales Order Processing

```python
from dynite import Dynite
from datetime import datetime, timedelta

client = Dynite(base_url="...", auth=("user", "pass"))

# Get recent sales orders
thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

orders = client.get_records("salesOrders", {
    "$filter": f"orderDate gt {thirty_days_ago}",
    "$expand": "customer,salesOrderLines",
    "$orderby": "orderDate desc"
})

total_value = 0
for order in orders:
    order_total = sum(line['lineAmount'] for line in order['salesOrderLines'])
    total_value += order_total
    print(f"Order {order['number']}: ${order_total:.2f}")

print(f"Total value of recent orders: ${total_value:.2f}")
```

## FAQ

### Q: Does Dynite support OAuth authentication?

**A:** Currently, Dynite only supports Basic Authentication. OAuth support may be added in future versions.

### Q: Can I use Dynite with on-premises Business Central?

**A:** Yes, as long as the Business Central instance exposes the OData v4.0 API over HTTP/HTTPS.

### Q: How does pagination work?

**A:** Dynite automatically follows OData `@odata.nextLink` responses to retrieve all pages. You don't need to handle pagination manually.

### Q: What are the rate limits?

**A:** Rate limits depend on your Business Central licensing and configuration. Dynite includes retry logic for transient failures.

### Q: Can I modify data (POST/PUT/DELETE)?

**A:** Currently, Dynite only supports read operations (GET). Write operations may be added in future versions.

### Q: How do I handle large result sets?

**A:** Use the `$top` parameter to limit results, and process data in batches to manage memory usage.

## Version History
Please see [CHANGELOG](CHANGELOG.md) for version history

## Support

- **Issues**: [GitHub Issues](https://github.com/prabhuakshay/dynite/issues)
- **Discussions**: [GitHub Discussions](https://github.com/prabhuakshay/dynite/discussions)

## Contributing

See the [Contributing](#contributing) section above for detailed guidelines.
