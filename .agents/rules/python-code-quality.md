---
trigger: always_on
---

# Python Code Quality Standard

## What we agreed

All Python code must be validated with **Ruff**, a fast linter and formatter that replaces multiple tools (Flake8, Black, isort, pyupgrade, etc.). Code must pass `ruff check` without errors and be formatted with `ruff format` before committing.

---

## Rules

1. **Run `ruff check . --fix && ruff format .` before every commit** - This lints and formats your code automatically
2. **Maximum line length is 100 characters** - Not 80, not 120
3. **Target Python 3.11 syntax** - Use modern Python features (f-strings, `|` for unions, built-in generics)
4. **Follow PEP 8 naming conventions** - Classes in `PascalCase`, functions in `snake_case`, constants in `UPPER_CASE`
5. **Organize imports in three groups** - stdlib, third-party, local (Ruff does this automatically)
6. **No unused imports or variables** - Ruff removes them automatically with `--fix`
7. **Use double quotes for strings** - `"hello"` not `'hello'` (unless technically required)

---

## Example

**✅ Do this:**
```python
# Correct: Modern Python 3.12, proper naming, organized imports
import json
import sys

import requests
from fastapi import FastAPI

from agent_net.common.logger import get_logger

MAX_RETRIES = 3  # Constants in UPPER_CASE

class UserService:  # Classes in PascalCase
    def __init__(self):
        self._logger = get_logger()  # Private with underscore
    
    def get_user(self, user_id: int) -> dict[str, str] | None:  # Functions in snake_case
        """Get user by ID."""
        if user_id > 0:
            message = f"Fetching user {user_id}"  # f-strings
            return {"name": "Alice", "id": str(user_id)}
        return None
```

**❌ Don't do this:**
```python
# Wrong: Old Python, bad naming, messy imports, unused code
from typing import Optional, Dict, List  # Old type hints
from agent_net.common.logger import get_logger
import requests  # Wrong order
import json
import unused_import  # Unused

maxRetries = 3  # Wrong: should be MAX_RETRIES

class userService:  # Wrong: should be UserService
    def GetUser(self, user_id):  # Wrong: should be get_user
        message = "Fetching user %s" % user_id  # Old string formatting
        return {"name": 'Alice'}  # Mixed quotes
```

---

### Quick Usage

**From project root:**
```bash
# Lint only (check for issues)
ruff check .

# Lint and auto-fix safe issues
ruff check . --fix

# Format code
ruff format .

# Recommended: do both
ruff check . --fix && ruff format .
```

---

### Configuration

Our Ruff configuration is in `pyproject.toml`:

---

## Why

**Speed**: Ruff is 10-100x faster than traditional Python linters (written in Rust)

**Simplicity**: One tool instead of managing Flake8, Black, isort, pyupgrade, flake8-bugbear, pep8-naming separately

**Consistency**: No debates about code style - everyone's code looks the same

**Safety**: Auto-fix only applies safe transformations that won't break your code

**Modern Python**: Encourages using Python 3.12 features, keeping code idiomatic and reducing technical debt

**Prevents bugs**: Catches common errors (unused variables, undefined names, mutable defaults) before they reach production

**Less PR churn**: Automatic formatting means fewer "fix spacing" comments in code reviews
