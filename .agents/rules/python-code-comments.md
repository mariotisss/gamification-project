---
trigger: always_on
---

# Code Comments Convention

## What we agreed

Use comments only when necessary, following Clean Code principles. Self-explanatory code with clear naming is always preferred over comments.

---

## Rules

1. Prefer creating a method with a clear name instead of adding docstring
2. Add comments only when the code cannot be made self-explanatory
3. Methods do not need comments explaining each parameter (unless they are part of a shared library)
4. Classes do not need detailed comments for every attribute (unless they are part of a shared library)
5. When comments are needed, explain **why** the code does something, not **what** it does

---

## Example

**✅ Do this:**
```python
def calculate_discount_for_premium_customers(total_amount, customer_tier):
    """Apply discount based on customer tier for purchases over $100."""
    if total_amount < 100:
        return 0
    
    return total_amount * TIER_DISCOUNT_RATES[customer_tier]

# Comment explaining a non-obvious business rule
# We keep inactive users for 90 days due to GDPR requirements
INACTIVE_USER_RETENTION_DAYS = 90
```

**❌ Don't do this:**
```python
def calc(amt, tier):
    # Calculate discount for customers
    # amt: the total amount
    # tier: customer tier level
    # Returns: discount amount
    if amt < 100:  # Check if amount is less than 100
        return 0   # Return zero if less than 100
    
    # Calculate discount by multiplying amount by tier rate
    return amt * TIER_DISCOUNT_RATES[tier]

class User:
    """User class.
    
    Attributes:
        id: The user identifier
        name: The user name
        email: The user email
    """
    def __init__(self, id, name, email):
        self.id = id        # User ID
        self.name = name    # User name
        self.email = email  # User email
```

---

## Why

- **Readable code is better than comments**: Well-named functions and variables are self-documenting and cannot become outdated like comments can
- **Comments can lie**: When code changes, comments often don't get updated, creating confusion
- **Less noise**: Excessive comments make code harder to read and maintain
- **Focus on the important**: When comments are rare, the ones that exist stand out and are more likely to be read
- **Exception for libraries**: Shared libraries need detailed documentation because they are used by multiple teams who may not be familiar with the implementation
