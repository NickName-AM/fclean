import pytest
from fclean import to_pascal_case, validate_name


def test_to_pascal_case_single_word():
    assert to_pascal_case("auth") == "Auth"


def test_to_pascal_case_snake():
    assert to_pascal_case("user_profile") == "UserProfile"


def test_to_pascal_case_with_digit():
    assert to_pascal_case("my_feature2") == "MyFeature2"


def test_to_pascal_case_multiple_underscores():
    assert to_pascal_case("my_long_feature_name") == "MyLongFeatureName"


def test_to_pascal_case_trailing_underscore():
    # "auth_".split("_") -> ["auth", ""] and "".capitalize() == "" so trailing underscore
    # produces no trailing character: "Auth" not "Auth_"
    assert to_pascal_case("auth_") == "Auth"


def test_to_pascal_case_digit_end_segment():
    assert to_pascal_case("feature2_auth") == "Feature2Auth"


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
