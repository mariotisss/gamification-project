# Project Rules

Full rules in `.agents/rules/*.md`. Summary below — all apply always.

## Code Comments (`python-code-comments.md`)
- Prefer self-explanatory code (clear names) over comments.
- Add comments only when code can't be made self-explanatory; explain **why**, not **what**.
- No per-parameter/per-attribute docstrings unless it's a shared library.

## Code Quality (`python-code-quality.md`)
- Max line length: 100. Target Python 3.11+ syntax.
- PEP 8 naming: `PascalCase` classes, `snake_case` functions, `UPPER_CASE` constants.
- Imports grouped: stdlib → third-party → local. No unused imports/vars.
- Use double quotes for strings.

## Named Arguments (`python-named-arguments.md`)
- Always use named arguments in function calls, even single-param.
- Exception: obvious built-ins (`len()`, `print()`, `str()`).
- Always type-annotate function definitions.

## No `None` Returns (`python-none-usage-restriction.md`)
- Functions/methods **must not return `None`** to external callers.
- Return empty equivalents instead:
  - Collections → `[]`, `set()`, `()`
  - Dicts → `{}`
  - Strings → `""`
  - Enums → `UNKNOWN` member
  - Numbers → `0`, `-1`, or domain-appropriate sentinel
- `None` is only allowed for **internal** class/method variables (typed as `T | None`).

## Strict Typing (`python-strict-typing.md`)
- All function signatures need parameter + return type hints (use `-> None` explicitly).
- Annotate variables, especially complex types.
- Modern syntax: `list[str]`, `dict[str, int]`, `str | None` (no `List`, `Dict`, `Optional`, `Union`).
- Avoid `Any`; use `TypeAlias` for reusable complex types.