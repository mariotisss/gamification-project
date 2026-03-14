---
trigger: always_on
---

# Strict Type Annotations in Python

## What we agreed

All Python code in the AI Agents domain **must use strict type annotations** for functions, variables, and complex data structures. This improves code quality, maintainability, and developer experience by catching type-related bugs early and enabling better IDE support.

---

## Rules

1. **All function signatures must include type hints** for parameters and return values
2. **Variable declarations should include type annotations**, especially for complex types (lists, dicts, custom classes)
3. **Use modern Python 3.11+ type syntax** - built-in generics like `list[str]`, `dict[str, int]` (not `List[str]`, `Dict[str, int]`)
4. **Use `|` for union types** - `str | None` instead of `Optional[str]` or `Union[str, None]`
5. **Use `None` for functions without return values** - explicitly type return as `-> None`
6. **Avoid `Any` type** - only use when absolutely necessary and document why
7. **Use `TypeAlias` for complex type definitions** - assign reusable type hints to descriptive names

---

## Examples

### Function Type Hints

**✅ Do this:**
```python
def process_message(message: str, user_id: int) -> dict[str, str]:
    """Process a message and return metadata."""
    return {
        "message": message,
        "user": str(user_id),
        "status": "processed"
    }

def fetch_user(user_id: int) -> dict[str, str] | None:
    """Fetch user by ID. Returns None if not found."""
    if user_id > 0:
        return {"name": "Alice", "id": str(user_id)}
    return None

def log_event(event: str, timestamp: float) -> None:
    """Log an event with timestamp."""
    print(f"{timestamp}: {event}")
```

**❌ Don't do this:**
```python
from typing import Optional, Dict, Union  # Don't use old typing imports

def process_message(message, user_id):  # Missing type hints
    return {"message": message, "user": str(user_id)}

def fetch_user(user_id: int) -> Optional[Dict[str, str]]:  # Old syntax
    if user_id > 0:
        return {"name": "Alice", "id": str(user_id)}
    return None

def log_event(event: str, timestamp: float):  # Missing return type
    print(f"{timestamp}: {event}")
```

---

### Variable Type Annotations

**✅ Do this:**
```python
# Simple types
count: int = 0
name: str = "Agent"
is_active: bool = True

# Collections with modern syntax
users: list[str] = ["Alice", "Bob"]
config: dict[str, str] = {"host": "localhost", "port": "8080"}
tags: set[str] = {"python", "ai", "agents"}

# Complex nested types
user_data: dict[str, list[int]] = {
    "alice": [1, 2, 3],
    "bob": [4, 5, 6]
}

# Custom classes
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

users_list: list[User] = []
```

**❌ Don't do this:**
```python
from typing import List, Dict, Set  # Don't import old typing classes

count = 0  # Missing type annotation for simple variable
users: List[str] = ["Alice", "Bob"]  # Old syntax
config: Dict[str, str] = {}  # Old syntax
tags: Set[str] = set()  # Old syntax

# No type hint for complex structure
user_data = {
    "alice": [1, 2, 3],
    "bob": [4, 5, 6]
}
```

---

### Union Types with `|`

**✅ Do this:**
```python
def get_value(key: str) -> str | int | None:
    """Get value which can be string, int, or None."""
    values = {"name": "Alice", "age": 30}
    return values.get(key)

def process(data: str | bytes) -> str:
    """Process string or bytes input."""
    if isinstance(data, bytes):
        return data.decode("utf-8")
    return data

# Multiple union types
Result = dict[str, str] | list[str] | None
```

**❌ Don't do this:**
```python
from typing import Optional, Union  # Don't use old union syntax

def get_value(key: str) -> Optional[Union[str, int]]:  # Old syntax
    values = {"name": "Alice", "age": 30}
    return values.get(key)

def process(data: Union[str, bytes]) -> str:  # Old syntax
    if isinstance(data, bytes):
        return data.decode("utf-8")
    return data
```

---

### Type Aliases for Complex Types

**✅ Do this:**
```python
from typing import TypeAlias

# Define reusable type aliases
UserId: TypeAlias = int
UserData: TypeAlias = dict[str, str | int]
MessageQueue: TypeAlias = list[tuple[str, float]]

def create_user(user_id: UserId, data: UserData) -> bool:
    """Create a user with given ID and data."""
    return True

def process_queue(queue: MessageQueue) -> None:
    """Process messages from the queue."""
    for message, timestamp in queue:
        print(f"{timestamp}: {message}")

# Complex nested types
AgentConfig: TypeAlias = dict[str, str | int | list[str]]
AgentRegistry: TypeAlias = dict[str, AgentConfig]
```

**❌ Don't do this:**
```python
# Repeating complex types without alias
def create_user(user_id: int, data: dict[str, str | int]) -> bool:
    return True

def update_user(user_id: int, data: dict[str, str | int]) -> bool:
    return True

def delete_user(user_id: int, data: dict[str, str | int]) -> bool:
    return True

# Hard to read nested types
def process_config(config: dict[str, str | int | list[str]]) -> dict[str, dict[str, str | int | list[str]]]:
    return {"agents": config}
```

---

### Class Type Annotations

**✅ Do this:**
```python
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Agent configuration with strict types."""
    name: str
    model: str
    temperature: float
    max_tokens: int
    tools: list[str]
    
class AgentService:
    """Service for managing agents."""
    
    def __init__(self, config: AgentConfig) -> None:
        self.config: AgentConfig = config
        self._cache: dict[str, str] = {}
        
    def run_agent(self, prompt: str, context: dict[str, str]) -> str:
        """Run agent with given prompt and context."""
        return f"Response for: {prompt}"
    
    def get_cached_response(self, key: str) -> str | None:
        """Get cached response if available."""
        return self._cache.get(key)
```

**❌ Don't do this:**
```python
class AgentConfig:
    """Agent configuration without types."""
    def __init__(self, name, model, temperature, max_tokens, tools):  # No types
        self.name = name
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools = tools
    
class AgentService:
    def __init__(self, config):  # No type hint
        self.config = config
        self._cache = {}  # No type annotation
        
    def run_agent(self, prompt, context):  # No types
        return f"Response for: {prompt}"
```

---

### Avoiding `Any` Type

**✅ Do this:**
```python
from typing import TypeAlias

# Use specific types
JsonValue: TypeAlias = str | int | float | bool | None | dict[str, "JsonValue"] | list["JsonValue"]

def parse_json(data: str) -> JsonValue:
    """Parse JSON string to typed value."""
    import json
    return json.loads(data)

# Use generics for flexibility
from typing import TypeVar

T = TypeVar("T")

def first_item(items: list[T]) -> T | None:
    """Get first item from list."""
    return items[0] if items else None
```

**❌ Don't do this:**
```python
from typing import Any

def parse_json(data: str) -> Any:  # Avoid Any without good reason
    import json
    return json.loads(data)

def process_data(data: Any) -> Any:  # Too generic, loses type safety
    return data
```

---

## Benefits

**Early Bug Detection**: Type-related errors are caught during development, not in production

**Better IDE Support**: Accurate autocompletion, parameter hints, and inline documentation

**Self-Documenting Code**: Function signatures clearly show expected inputs and outputs

**Safer Refactoring**: Type hints help identify all places that need changes

**Improved Collaboration**: Clear contracts between components and agents

**Easier Onboarding**: New developers understand code structure faster

---

## Type Checking Tools

Our type annotations are validated through:

1. **IDE Support** - VS Code with Pylance or PyCharm provide real-time type checking
2. **Ruff** - Already configured in `pyproject.toml` to enforce type hints
3. **Code Reviews** - All PRs must include proper type annotations

---

## Why

Type annotations are a key part of modern Python development:

- **Python 3.5+** introduced type hints (PEP 484)
- **Python 3.9+** enabled built-in generic types
- **Python 3.10+** introduced the `|` union operator
- **Python 3.11+** improves type checking performance

Our multi-agent architecture requires **clear interfaces** between components. Type annotations provide compile-time guarantees that agents communicate with correct data structures, reducing runtime errors and debugging time.

By enforcing strict typing, we align with industry best practices and create a maintainable codebase that scales with the organization.

---

## Related Documentation

- [Python Code Quality Standard](python-code-quality.md) - Covers Ruff linting and formatting requirements
