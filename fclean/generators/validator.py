import sys
import re


def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase for Dart class names.

    Examples:
        user_profile -> UserProfile
        auth -> Auth
        my_feature2 -> MyFeature2
    """
    return "".join(
        word[:1].upper() + word[1:] for word in name.split("_") if word
    )


_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


def validate_name(name: str) -> None:
    """Validate a feature or entity name. Exits 1 with a clear message if invalid."""
    if not _NAME_RE.fullmatch(name):
        print(
            f"Error: Invalid name '{name}'. "
            "Names must start with a lowercase letter and contain only [a-z0-9_].",
            file=sys.stderr,
        )
        sys.exit(1)
