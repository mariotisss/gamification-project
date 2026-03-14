---
trigger: always_on
---

# Named Arguments in Function Calls

## What we agreed

Always use named arguments when calling functions to improve code readability and maintainability.

---

## Rules

1. Use named arguments for all function calls, even for functions with a single parameter
2. The only exception is for very common built-in functions where the meaning is obvious (e.g., `len()`, `print()`, `str()`)
3. When defining functions, always use type annotations to make the expected types clear
4. Apply this rule to both internal function calls and external library calls where practical

---

## Example

**✅ Do this:**
```python
# Function definition
def process_data(data: str, timeout: int, retry: bool) -> None:
    pass

# Function call - explicit and clear
process_data(data="user_input", timeout=30, retry=True)

# Single parameter - still use named argument
def calculate_total(amount: float) -> float:
    return amount * 1.21

total = calculate_total(amount=100.0)
```

**❌ Don't do this:**
```python
# Function definition
def process_data(data: str, timeout: int, retry: bool) -> None:
    pass

# Function call - unclear what each value represents
process_data("user_input", 30, True)

# Single parameter - positional argument
def calculate_total(amount: float) -> float:
    return amount * 1.21

total = calculate_total(100.0)
```

---

## Why

**Readability**: Named arguments make it immediately clear what each value represents without needing to check the function signature.

**Maintainability**: If the function signature changes (e.g., parameter order is modified or new parameters are added), named arguments prevent silent bugs and make refactoring safer.

**Self-documenting code**: The function call itself documents what each argument does, reducing the need for additional comments.

**Error prevention**: Positional arguments can lead to subtle bugs when parameters are accidentally swapped, especially with parameters of the same type. Named arguments eliminate this risk.

**IDE support**: Modern IDEs can better validate and autocomplete named arguments, catching errors at development time rather than runtime.
