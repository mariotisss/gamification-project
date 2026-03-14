---
trigger: always_on
---

# Python None Usage Restriction Standard

## What we agreed

**`None` values must be restricted to class and method variable scope only**. Functions and methods **must not return `None` values** to external callers. Instead, return appropriate empty values for each data type to create more robust, predictable APIs that reduce null pointer errors and improve code reliability.

---

## Rules

1. **Functions and methods must not return `None`** - Use appropriate empty values instead
2. **For collections (lists, sets, tuples), return empty collections** - `[]`, `set()`, `()`
3. **For dictionaries/mappings, return empty dictionaries** - `{}`
4. **For strings, return empty strings** - `""`
5. **For enumerations, return `UNKNOWN` or equivalent default value**
6. **For numbers, evaluate case-by-case** - use `0`, `-1`, or appropriate sentinel value
7. **`None` is allowed only for internal variables** within class and method scope
8. **Use type annotations with union types** when `None` is internal: `str | None`

---

## Examples

### Collections and Mappings

**✅ Do this:**
```python
def get_user_permissions(user_id: int) -> list[str]:
    """Get user permissions. Returns empty list if no permissions."""
    if not user_id:
        return []  # Empty list, not None

    permissions = fetch_permissions_from_db(user_id)
    return permissions if permissions else []

def get_user_metadata(user_id: int) -> dict[str, str]:
    """Get user metadata. Returns empty dict if no metadata."""
    if not user_id:
        return {}  # Empty dict, not None

    metadata = fetch_metadata_from_db(user_id)
    return metadata if metadata else {}

def get_user_tags(user_id: int) -> set[str]:
    """Get user tags. Returns empty set if no tags."""
    if not user_id:
        return set()  # Empty set, not None

    tags = fetch_tags_from_db(user_id)
    return tags if tags else set()
```

**❌ Don't do this:**
```python
def get_user_permissions(user_id: int) -> list[str] | None:
    """Don't return None for collections."""
    if not user_id:
        return None  # ❌ Should return []

    permissions = fetch_permissions_from_db(user_id)
    return permissions  # Could be None

def get_user_metadata(user_id: int) -> dict[str, str] | None:
    """Don't return None for mappings."""
    if not user_id:
        return None  # ❌ Should return {}
```

---

### String Values

**✅ Do this:**
```python
def get_user_name(user_id: int) -> str:
    """Get user name. Returns empty string if not found."""
    if not user_id:
        return ""  # Empty string, not None

    user_name: str | None = fetch_name_from_db(user_id)  # Internal None allowed
    return user_name if user_name else ""

def format_address(street: str, city: str, country: str) -> str:
    """Format address. Returns empty string if no data."""
    if not street and not city and not country:
        return ""  # Empty string for no data

    parts: list[str] = []
    if street:
        parts.append(street)
    if city:
        parts.append(city)
    if country:
        parts.append(country)

    return ", ".join(parts)
```

**❌ Don't do this:**
```python
def get_user_name(user_id: int) -> str | None:
    """Don't return None for strings."""
    if not user_id:
        return None  # ❌ Should return ""

    return fetch_name_from_db(user_id)  # Could return None
```

---

### Enumerations

**✅ Do this:**
```python
from enum import Enum

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"  # Default for missing values

def get_user_status(user_id: int) -> UserStatus:
    """Get user status. Returns UNKNOWN if not determinable."""
    if not user_id:
        return UserStatus.UNKNOWN  # Default enum value

    status_str: str | None = fetch_status_from_db(user_id)  # Internal None allowed

    if status_str == "active":
        return UserStatus.ACTIVE
    elif status_str == "inactive":
        return UserStatus.INACTIVE
    elif status_str == "suspended":
        return UserStatus.SUSPENDED

    return UserStatus.UNKNOWN  # Default for unrecognized values

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    UNKNOWN = 0  # Default numeric value

def get_task_priority(task_id: int) -> Priority:
    """Get task priority. Returns UNKNOWN if not set."""
    if not task_id:
        return Priority.UNKNOWN

    priority_value: int | None = fetch_priority_from_db(task_id)

    for priority in Priority:
        if priority.value == priority_value:
            return priority

    return Priority.UNKNOWN
```

**❌ Don't do this:**
```python
def get_user_status(user_id: int) -> UserStatus | None:
    """Don't return None for enums."""
    if not user_id:
        return None  # ❌ Should return UserStatus.UNKNOWN

    return fetch_status_from_db(user_id)  # Could return None
```

---

### Numeric Values (Case-by-Case)

**✅ Do this:**
```python
def get_user_score(user_id: int) -> int:
    """Get user score. Returns 0 for new/unknown users."""
    if not user_id:
        return 0  # Zero is appropriate default for scores

    score: int | None = fetch_score_from_db(user_id)  # Internal None allowed
    return score if score is not None else 0

def get_user_age(user_id: int) -> int:
    """Get user age. Returns -1 if unknown (since 0 is valid age)."""
    if not user_id:
        return -1  # -1 indicates unknown age

    age: int | None = fetch_age_from_db(user_id)  # Internal None allowed
    return age if age is not None else -1

def get_retry_count() -> int:
    """Get retry count. Returns 0 as safe default."""
    return 0  # 0 is safe default for retry counts

def get_timeout_seconds() -> float:
    """Get timeout. Returns 30.0 as reasonable default."""
    return 30.0  # Default timeout value
```

**❌ Don't do this:**
```python
def get_user_score(user_id: int) -> int | None:
    """Don't return None for numbers."""
    if not user_id:
        return None  # ❌ Should return appropriate default
```

---

### Internal None Usage (Allowed)

**✅ Do this:**
```python
class UserService:
    """Service for user operations."""

    def __init__(self) -> None:
        self._cache: dict[int, str] | None = None  # Internal None allowed
        self._connection: DatabaseConnection | None = None  # Internal None allowed

    def get_user_data(self, user_id: int) -> dict[str, str]:
        """Get user data. Returns empty dict if not found."""
        # Internal None handling is allowed
        cached_data: dict[str, str] | None = self._get_from_cache(user_id)
        if cached_data is not None:
            return cached_data

        # Fetch from database
        db_data: dict[str, str] | None = self._fetch_from_db(user_id)
        if db_data is not None:
            self._save_to_cache(user_id, db_data)
            return db_data

        # Return empty dict, not None
        return {}

    def _get_from_cache(self, user_id: int) -> dict[str, str] | None:
        """Internal method can return None."""
        if self._cache is None:
            return None
        return self._cache.get(user_id)

    def _fetch_from_db(self, user_id: int) -> dict[str, str] | None:
        """Internal method can return None."""
        # Database might return None for missing records
        return self._connection.fetch_user(user_id) if self._connection else None
```

---

### Complex Data Structures

**✅ Do this:**
```python
from typing import TypeAlias
from dataclasses import dataclass

@dataclass
class UserProfile:
    """User profile with default values."""
    name: str = ""
    email: str = ""
    tags: list[str] = None  # Will be converted to empty list

    def __post_init__(self) -> None:
        """Ensure no None values in public interface."""
        if self.tags is None:
            self.tags = []

def get_user_profile(user_id: int) -> UserProfile:
    """Get user profile. Returns profile with empty values if not found."""
    if not user_id:
        return UserProfile()  # Empty profile, not None

    # Internal processing may use None
    profile_data: dict[str, str] | None = fetch_profile_from_db(user_id)

    if profile_data is None:
        return UserProfile()  # Empty profile

    return UserProfile(
        name=profile_data.get("name", ""),
        email=profile_data.get("email", ""),
        tags=profile_data.get("tags", [])
    )

def get_user_friends(user_id: int) -> list[UserProfile]:
    """Get user friends. Returns empty list if none."""
    if not user_id:
        return []  # Empty list, not None

    friend_ids: list[int] | None = fetch_friend_ids_from_db(user_id)
    if not friend_ids:
        return []  # Empty list for no friends

    friends: list[UserProfile] = []
    for friend_id in friend_ids:
        friend_profile = get_user_profile(friend_id)
        friends.append(friend_profile)  # Always valid UserProfile

    return friends
```

---

## Benefits

**Eliminates Null Pointer Errors**: Callers never receive unexpected `None` values that could cause crashes

**Simplifies Client Code**: No need for constant `if result is not None:` checks in calling code

**Improves API Predictability**: Functions always return usable values, even if empty

**Reduces Debugging Time**: Fewer runtime errors from attempting to use `None` values

**Better Type Safety**: Cleaner type signatures without complex union types

**Consistent Behavior**: All functions follow the same pattern for handling missing data

---

## Why

**Industry Best Practices**: Null safety is a key principle in modern language design

**Agent Architecture Requirements**: Our multi-agent system requires reliable data flow between components without null-related failures

**Error Reduction**: Null pointer exceptions are among the most common runtime errors in software

**Code Readability**: Cleaner APIs without complex null handling logic scattered throughout the codebase

**Testing Simplicity**: Easier to write comprehensive tests when functions always return valid values

**Performance**: Eliminates runtime null checks in calling code, improving execution speed

This standard aligns with functional programming principles where functions should be total (always return a value) rather than partial (might return nothing).
