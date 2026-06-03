import sys
import pytest
sys.path.insert(0, ".")
from fclean import to_pascal_case, validate_name  # NOTE: import path changes after Phase 2 package restructure


def test_to_pascal_case_single_word():
    assert to_pascal_case("auth") == "Auth"


def test_to_pascal_case_snake():
    assert to_pascal_case("user_profile") == "UserProfile"


def test_to_pascal_case_with_digit():
    assert to_pascal_case("my_feature2") == "MyFeature2"


def test_validate_name_valid_passes():
    validate_name("auth")         # must not raise
    validate_name("user_profile")


def test_validate_name_invalid_exits():
    with pytest.raises(SystemExit) as exc_info:
        validate_name("../evil")
    assert exc_info.value.code == 1


def test_validate_name_uppercase_exits():
    with pytest.raises(SystemExit):
        validate_name("User")


def test_validate_name_leading_digit_exits():
    with pytest.raises(SystemExit):
        validate_name("1auth")


def test_validate_name_empty_exits():
    with pytest.raises(SystemExit):
        validate_name("")
